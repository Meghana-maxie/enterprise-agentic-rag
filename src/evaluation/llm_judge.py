"""Claude-powered LLM-as-a-Judge for offline batch evaluation and LLMOps benchmarking."""

import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
# Keep anthropic import for potential direct use in AnthropicClient
import anthropic
from config.settings import settings

# Providerâ€‘agnostic LLM client abstractions
from src.llm.base_client import BaseLLMClient, OllamaClient, AnthropicClient

class BenchmarkMetrics(BaseModel):
    """Evaluation metrics for a single query."""
    faithfulness: float = Field(ge=0.0, le=1.0)
    answer_relevance: float = Field(ge=0.0, le=1.0)
    context_precision: float = Field(ge=0.0, le=1.0)
    context_recall: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""


class ClaudeLLMJudge:
    """Offline batch evaluation judge leveraging a LLM provider."""

    def __init__(self, api_key: str = settings.ANTHROPIC_API_KEY, model: str = settings.ANTHROPIC_MODEL):
        self.api_key = api_key
        self.model = model
        # Initialise the appropriate client based on settings.LLM_PROVIDER
        if settings.LLM_PROVIDER == "ollama":
            self.client: BaseLLMClient = OllamaClient()
        elif settings.LLM_PROVIDER == "anthropic":
            # Use Anthropic client only when a real key is supplied; otherwise None (fallback will trigger heuristic)
            self.client = AnthropicClient(api_key=api_key, model=model) if api_key and api_key != "mock-key" else None
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER}")
    def evaluate_sample(
        self,
        query: str,
        retrieved_contexts: List[str],
        generated_answer: str,
        ground_truth: str
    ) -> BenchmarkMetrics:
        """Score Faithfulness, Answer Relevance, Context Precision, and Context Recall."""
        prompt = f"""You are an expert AI evaluation judge for an Enterprise RAG system.
Evaluate the generated answer and retrieved context against the user query and ground truth.

[USER QUERY]: {query}
[GROUND TRUTH]: {ground_truth}
[RETRIEVED CONTEXTS]:
{json.dumps(retrieved_contexts, indent=2)}
[GENERATED ANSWER]: {generated_answer}

Score the following metrics on a continuous scale from 0.00 to 1.00:
1. Faithfulness: Is every claim in the generated answer strictly supported by the retrieved contexts?
2. Answer Relevance: Does the generated answer directly address the user query without unnecessary fluff?
3. Context Precision: Are the retrieved contexts relevant and focused on answering the query?
4. Context Recall: Do the retrieved contexts contain all facts needed to match the ground truth?

Output ONLY a single valid JSON object in this exact schema, with each field appearing EXACTLY ONCE. The values below are placeholder types, NOT the answer â€” compute your own score for THIS specific query/answer/context. Keep "reasoning" to ONE short sentence, no more than 20 words:
{{
  "faithfulness": <your computed float between 0.0 and 1.0>,
  "answer_relevance": <your computed float between 0.0 and 1.0>,
  "context_precision": <your computed float between 0.0 and 1.0>,
  "context_recall": <your computed float between 0.0 and 1.0>,
  "reasoning": "<one short sentence, max 20 words>"
}}"""

        for attempt in range(2):
            try:
                raw_text = self.client.generate(
                    system_prompt="You are an objective evaluation evaluator. Return only JSON.",
                    user_prompt=prompt,
                    max_tokens=800
                )
                print(f"=== RAW OLLAMA OUTPUT ===\n{raw_text}\n=========================")
                json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    return BenchmarkMetrics(
                        faithfulness=float(data.get("faithfulness", 0.8)),
                        answer_relevance=float(data.get("answer_relevance", 0.8)),
                        context_precision=float(data.get("context_precision", 0.8)),
                        context_recall=float(data.get("context_recall", 0.8)),
                        reasoning=data.get("reasoning", "")
                    )
                raise ValueError(f"No JSON object found in model response: {raw_text}")
            except Exception as e:
                print(f"LLM judge evaluation attempt {attempt + 1} failed: {e}")
                if attempt == 1:
                    raise


    @staticmethod
    def _heuristic_fallback(
        query: str,
        retrieved_contexts: List[str],
        generated_answer: str,
        ground_truth: str
    ) -> BenchmarkMetrics:
        """Deterministic fallback scoring for offline testing without API connection."""
        combined_ctx = " ".join(retrieved_contexts).lower()
        ans_lower = generated_answer.lower()
        gt_tokens = set(re.findall(r"\w{4,}", ground_truth.lower()))
        ans_tokens = set(re.findall(r"\w{4,}", ans_lower))

        recall = len(gt_tokens.intersection(ans_tokens)) / max(len(gt_tokens), 1)
        precision = len(ans_tokens.intersection(set(re.findall(r"\w{4,}", combined_ctx)))) / max(len(ans_tokens), 1)

        return BenchmarkMetrics(
            faithfulness=min(1.0, precision + 0.1),
            answer_relevance=min(1.0, recall + 0.15),
            context_precision=min(1.0, precision),
            context_recall=min(1.0, recall),
            reasoning="Heuristic fallback computation based on lexical token alignment."
        )
