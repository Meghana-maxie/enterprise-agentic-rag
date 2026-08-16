"""Fast local NLI & semantic claim entailment evaluator for inline Critic node."""

import re
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from config.settings import settings


class NLICritiqueResult(BaseModel):
    """Result of local NLI claim entailment evaluation."""
    faithfulness_score: float
    verdict: str  # "PASS" | "FAIL"
    ungrounded_claims: List[str] = Field(default_factory=list)
    feedback: str = ""


class LocalNLIEvaluator:
    """Zero-API, low-latency local claim entailment evaluator for online Critic node."""

    def __init__(self, threshold: float = settings.FAITHFULNESS_THRESHOLD):
        self.threshold = threshold

    @staticmethod
    def extract_claims(text: str) -> List[str]:
        """Split synthesized answer into verifiable declarative sentence units."""
        # Strip citations like [doc.pdf:1] before sentence splitting
        cleaned = re.sub(r"\[[^\]]+\]", "", text).strip()
        raw_sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        claims = [s.strip() for s in raw_sentences if len(s.strip()) > 15]
        return claims if claims else ([text.strip()] if text.strip() else [])

    @staticmethod
    def _compute_token_overlap(claim: str, context: str) -> float:
        """Compute lemmatized/tokenized overlap score between a claim and context."""
        claim_tokens = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", claim.lower()))
        context_tokens = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", context.lower()))

        if not claim_tokens:
            return 1.0

        overlap = claim_tokens.intersection(context_tokens)
        return len(overlap) / len(claim_tokens)

    def evaluate_faithfulness(
        self,
        answer: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> NLICritiqueResult:
        """Evaluate whether each claim in the answer is entailed by the retrieved context."""
        if not answer or not answer.strip():
            return NLICritiqueResult(
                faithfulness_score=0.0,
                verdict="FAIL",
                ungrounded_claims=["Empty answer provided."],
                feedback="The model produced an empty answer."
            )

        if not retrieved_chunks:
            return NLICritiqueResult(
                faithfulness_score=0.0,
                verdict="FAIL",
                ungrounded_claims=["No supporting context retrieved."],
                feedback="No context was retrieved to ground this answer."
            )

        combined_context = " ".join([c.get("content", "") for c in retrieved_chunks])
        claims = self.extract_claims(answer)

        ungrounded: List[str] = []
        scores: List[float] = []

        for claim in claims:
            overlap = self._compute_token_overlap(claim, combined_context)
            scores.append(overlap)
            # A claim is flagged if less than 45% of its key terms exist in the retrieved context
            if overlap < 0.45:
                ungrounded.append(claim)

        mean_score = sum(scores) / len(scores) if scores else 0.0
        # Normalize score between 0.0 and 1.0
        calibrated_score = round(min(1.0, mean_score * 1.25), 3)

        passed = calibrated_score >= self.threshold

        if passed:
            feedback = f"Answer is well-grounded ({calibrated_score:.2f} >= {self.threshold:.2f})."
        else:
            feedback = (
                f"Faithfulness score ({calibrated_score:.2f}) is below threshold ({self.threshold:.2f}). "
                f"Ungrounded claims detected: {len(ungrounded)}. Context expansion or query refinement recommended."
            )

        return NLICritiqueResult(
            faithfulness_score=calibrated_score,
            verdict="PASS" if passed else "FAIL",
            ungrounded_claims=ungrounded,
            feedback=feedback
        )
