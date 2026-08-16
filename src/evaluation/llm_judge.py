"""Claude-powered LLM-as-a-Judge for offline batch evaluation and LLMOps benchmarking."""

import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import anthropic
from config.settings import settings


class BenchmarkMetrics(BaseModel):
    """Evaluation metrics for a single query."""
    faithfulness: float = Field(ge=0.0, le=1.0)
    answer_relevance: float = Field(ge=0.0, le=1.0)
    context_precision: float = Field(ge=0.0, le=1.0)
    context_recall: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""


class ClaudeLLMJudge:
    """Offline batch evaluation judge leveraging Claude Haiku."""

    def __init__(self, api_key: str = settings.ANTHROPIC_API_KEY, model: str = settings.ANTHROPIC_MODEL):
        self.api_key = api_key
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key) if api_key and api_key != "mock-key" else None

    def evaluate_sample(
        self,
        query: str,
        retrieved_contexts: List[str],
        generated_answer: str,
        ground_truth: str
    ) -> BenchmarkMetrics:
        """Score Faithfulness, Answer Relevance, Context Precision, and Context Recall."""
        if not self.client:
            # Fallback heuristic calculation if API key is not configured
            return self._heuristic_fallback(query, retrieved_contexts, generated_answer, ground_truth)

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

Output ONLY a valid JSON object in this exact schema:
{{
  "faithfulness": 0.95,
  "answer_relevance": 0.90,
  "context_precision": 0.85,
  "context_recall": 0.92,
  "reasoning": "Concise 1-2 sentence justification"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.0,
                system="You are an objective evaluation evaluator. Return only JSON.",
                messages=[{"role": "user", "content": prompt}]
            )
            raw_text = response.content[0].text
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
        except Exception as e:
            pass

        return self._heuristic_fallback(query, retrieved_contexts, generated_answer, ground_truth)

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
