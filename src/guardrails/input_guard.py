"""Input guardrail for deterministic PII redaction and prompt injection prevention."""

from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel, Field
from config.pii_patterns import PII_PATTERNS, INJECTION_SIGNATURES


class InputGuardResult(BaseModel):
    """Result of input sanitization and safety assessment."""
    is_safe: bool
    sanitized_text: str
    redacted_pii: List[str] = Field(default_factory=list)
    refusal_reason: Optional[str] = None


class InputGuardrail:
    """Pre-execution security gatekeeper."""

    def __init__(self):
        self.pii_patterns = PII_PATTERNS
        self.injection_signatures = INJECTION_SIGNATURES

    def detect_prompt_injection(self, text: str) -> Tuple[bool, Optional[str]]:
        """Check if input text matches known adversarial prompt injection patterns."""
        for pattern in self.injection_signatures:
            if pattern.search(text):
                return True, f"Prompt injection signature detected: '{pattern.pattern}'"
        return False, None

    def redact_pii(self, text: str) -> Tuple[str, List[str]]:
        """Identify and redact PII entities with structured placeholders."""
        redacted_text = text
        detected: List[str] = []

        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(redacted_text)
            if matches:
                detected.append(pii_type)
                redacted_text = pattern.sub(f"[REDACTED_{pii_type}]", redacted_text)

        return redacted_text, detected

    def sanitize(self, raw_query: str) -> InputGuardResult:
        """Run complete input guardrail pipeline."""
        # 1. Prompt Injection Detection
        is_injection, reason = self.detect_prompt_injection(raw_query)
        if is_injection:
            return InputGuardResult(
                is_safe=False,
                sanitized_text=raw_query,
                redacted_pii=[],
                refusal_reason=reason or "Security violation: potential prompt injection detected."
            )

        # 2. PII Detection & Redaction
        sanitized_query, pii_detected = self.redact_pii(raw_query)

        return InputGuardResult(
            is_safe=True,
            sanitized_text=sanitized_query,
            redacted_pii=pii_detected,
            refusal_reason=None
        )
