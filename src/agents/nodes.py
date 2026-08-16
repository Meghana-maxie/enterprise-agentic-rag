"""LangGraph node definitions for enterprise agentic RAG pipeline."""

import json
import re
from typing import Dict, Any, List
import anthropic
from src.llm.base_client import BaseLLMClient, OllamaClient, AnthropicClient
from src.agents.state import AgentState
from src.guardrails.input_guard import InputGuardrail
from src.guardrails.output_guard import OutputGuardrail
from src.retrieval.hybrid_engine import HybridSearchEngine
from src.evaluation.nli_evaluator import LocalNLIEvaluator
from config.settings import settings


class AgentNodeRunner:
    """Manages execution of all LangGraph nodes."""

    def __init__(
        self,
        hybrid_engine: HybridSearchEngine | None = None,
        input_guard: InputGuardrail | None = None,
        output_guard: OutputGuardrail | None = None,
        nli_evaluator: LocalNLIEvaluator | None = None,
    ):
        self.hybrid_engine = hybrid_engine or HybridSearchEngine()
        self.input_guard = input_guard or InputGuardrail()
        self.output_guard = output_guard or OutputGuardrail()
        self.nli_evaluator = nli_evaluator or LocalNLIEvaluator()

        self.anthropic_client = None
        if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "mock-key":
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            except Exception:
                self.anthropic_client = None
        # Provider‑agnostic client (default Ollama)
        if settings.LLM_PROVIDER == "ollama":
            self.llm_client: BaseLLMClient = OllamaClient()
        elif settings.LLM_PROVIDER == "anthropic":
            self.llm_client = AnthropicClient()
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER}")

    def _call_claude(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        """Helper to invoke Claude Haiku with robust error handling and mock fallback."""
        if not self.anthropic_client:
            # No Anthropic client – delegate to the generic client (Ollama or other)
            return self.llm_client.generate(system_prompt, user_prompt, max_tokens)

        try:
            response = self.anthropic_client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=max_tokens,
                temperature=settings.LLM_TEMPERATURE,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            # Fallback to deterministic synthesis if API fails or rate-limits
            return f"[API Fallback Response]: Generated answer based on context. Error: {str(e)}"

   
    # 1. Input Guardrail Node
    def input_guard_node(self, state: AgentState) -> Dict[str, Any]:
        """Sanitize query, strip PII, and detect adversarial prompt injection."""
        raw_query = state.get("raw_query", "")
        result = self.input_guard.sanitize(raw_query)

        trace = list(state.get("execution_trace", []))
        trace.append(f"InputGuard: is_safe={result.is_safe}, pii_count={len(result.redacted_pii)}")

        return {
            "sanitized_query": result.sanitized_text,
            "is_safe": result.is_safe,
            "refusal_reason": result.refusal_reason,
            "redacted_pii": result.redacted_pii,
            "execution_trace": trace,
        }

    # 2. Router & Query Transform Node
    def router_node(self, state: AgentState) -> Dict[str, Any]:
        """Classify user intent (Direct vs. RAG) and perform query expansion."""
        sanitized_query = state.get("sanitized_query", "")
        trace = list(state.get("execution_trace", []))

        # Check if critique feedback is present (retry loop)
        critic_feedback = state.get("critic_feedback")
        retry_prompt_mod = ""
        if critic_feedback:
            retry_prompt_mod = f"\nNote: Previous retrieval had poor grounding ({critic_feedback}). Expand query with broader keywords."

        system_prompt = """You are a smart query router for an enterprise AI assistant.
Determine whether the user query requires retrieval from the enterprise knowledge base or can be answered directly.
If it requires knowledge retrieval, output 'rag'. If it's a general greeting or basic math/logic, output 'direct'.
Also optimize the query by expanding technical synonyms or rewriting for better keyword matching.

Respond ONLY with valid JSON:
{"route": "direct" | "rag", "transformed_query": "expanded query text"}"""

        user_prompt = f"User Query: {sanitized_query}{retry_prompt_mod}"
        raw_response = self._call_claude(system_prompt, user_prompt, max_tokens=200)

        route = "rag"
        transformed_query = sanitized_query
        try:
            json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                route = parsed.get("route", "rag")
                transformed_query = parsed.get("transformed_query", sanitized_query)
        except Exception:
            route = "rag"

        trace.append(f"RouterNode: route={route}, query='{transformed_query}'")

        return {
            "route": route,
            "transformed_query": transformed_query,
            "execution_trace": trace,
        }

    # 3. Hybrid Retrieval & Rerank Node
    def retrieval_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute Dense + BM25 search with RRF and Local Cross-Encoder Reranking."""
        query = state.get("transformed_query") or state.get("sanitized_query", "")
        trace = list(state.get("execution_trace", []))

        # Execute hybrid search with local reranking
        reranked_chunks = self.hybrid_engine.search(
            query=query,
            retrieval_limit=settings.TOP_K_RETRIEVAL,
            rerank_limit=settings.TOP_K_RERANK
        )

        trace.append(f"RetrievalNode: retrieved_count={len(reranked_chunks)}")

        return {
            "retrieved_chunks": reranked_chunks,
            "reranked_chunks": reranked_chunks,
            "execution_trace": trace,
        }

    # 4. Synthesis & Strict Citation Node
    def synthesis_node(self, state: AgentState) -> Dict[str, Any]:
        """Generate grounded answer using Claude Haiku with strict bracket citation formatting."""
        route = state.get("route", "rag")
        sanitized_query = state.get("sanitized_query", "")
        reranked_chunks = state.get("reranked_chunks", [])
        trace = list(state.get("execution_trace", []))

        if route == "direct":
            system_prompt = "You are a concise, professional enterprise AI assistant. Answer directly and politely."
            answer = self._call_claude(system_prompt, sanitized_query, max_tokens=500)
            trace.append("SynthesisNode: direct response generated")
            return {
                "synthesized_answer": answer,
                "execution_trace": trace,
            }

        # Build context blocks with explicit source IDs
        context_blocks = []
        for c in reranked_chunks:
            doc = c.get("doc_name", "document")
            page = c.get("page_number", 1)
            content = c.get("content", "")
            context_blocks.append(f"--- [Source: {doc}, Page: {page}] ---\n{content}")

        combined_context = "\n\n".join(context_blocks)

        system_prompt = """You are an Enterprise AI Knowledge Assistant.
Answer the user's question using ONLY the provided context blocks.
Rules:
1. Every factual statement MUST be backed by an inline citation format: [doc_name:page_number] (e.g. [cloud_architecture.md:1]).
2. If the context does not contain the answer, explicitly state that the information is unavailable in the enterprise knowledge base. Do NOT hallucinate.
3. Keep the answer structured, clear, and professional."""

        user_prompt = f"""[QUESTION]: {sanitized_query}

[DOC_CONTEXT]:
{combined_context}

[ANSWER]:"""

        synthesized_text = self._call_claude(system_prompt, user_prompt, max_tokens=settings.LLM_MAX_TOKENS)
        trace.append(f"SynthesisNode: synthesized answer ({len(synthesized_text)} chars)")

        return {
            "synthesized_answer": synthesized_text,
            "execution_trace": trace,
        }

    # 5. Critic & Entailment Evaluation Node
    def critic_node(self, state: AgentState) -> Dict[str, Any]:
        """Evaluate claim entailment locally with LocalNLIEvaluator."""
        route = state.get("route", "rag")
        trace = list(state.get("execution_trace", []))

        # Direct routes do not require retrieval entailment check
        if route == "direct":
            trace.append("CriticNode: skipped for direct route")
            return {
                "faithfulness_score": 1.0,
                "critic_verdict": "PASS",
                "critic_feedback": "Direct route pass.",
                "execution_trace": trace,
            }

        answer = state.get("synthesized_answer", "")
        reranked_chunks = state.get("reranked_chunks", [])
        retry_count = state.get("retry_count", 0)

        # Run fast local NLI evaluation
        eval_result = self.nli_evaluator.evaluate_faithfulness(answer, reranked_chunks)

        trace.append(
            f"CriticNode: verdict={eval_result.verdict}, score={eval_result.faithfulness_score:.2f}, retry_count={retry_count}"
        )

        return {
            "faithfulness_score": eval_result.faithfulness_score,
            "critic_verdict": eval_result.verdict,
            "critic_feedback": eval_result.feedback,
            "retry_count": retry_count if eval_result.verdict == "PASS" else retry_count + 1,
            "execution_trace": trace,
        }

    # 6. Output Guardrail Node
    def output_guard_node(self, state: AgentState) -> Dict[str, Any]:
        """Final gatekeeper verifying citation correctness and schema conformity."""
        answer = state.get("synthesized_answer", "")
        chunks = state.get("reranked_chunks", [])
        faithfulness_score = state.get("faithfulness_score", 1.0)
        trace = list(state.get("execution_trace", []))

        guard_result = self.output_guard.validate(
            answer_text=answer,
            retrieved_chunks=chunks,
            faithfulness_score=faithfulness_score,
            faithfulness_threshold=settings.FAITHFULNESS_THRESHOLD
        )

        trace.append(
            f"OutputGuard: valid={guard_result.is_valid}, verified_citations={len(guard_result.verified_citations)}, warnings={len(guard_result.warnings)}"
        )

        return {
            "synthesized_answer": guard_result.sanitized_response,
            "verified_citations": [c.model_dump() for c in guard_result.verified_citations],
            "invalid_citations": guard_result.invalid_citations,
            "guardrail_warnings": guard_result.warnings,
            "execution_trace": trace,
        }
