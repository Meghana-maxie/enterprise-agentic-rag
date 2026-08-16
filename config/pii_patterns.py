"""Compiled regular expression patterns and heuristic rules for deterministic guardrails."""

import re
from typing import Dict, Pattern, List

# PII Detection and Redaction Patterns
PII_PATTERNS: Dict[str, Pattern] = {
    "SSN": re.compile(r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b"),
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "PHONE_US": re.compile(r"\b(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "CREDIT_CARD": re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b"),
    "API_KEY": re.compile(r"(?i)\b(?:api[_-]?key|secret[_-]?key|auth[_-]?token|bearer)\s*[:=]\s*['\"]?([A-Za-z0-9_\-\.]{16,})['\"]?"),
    "GENERIC_KEY_HEX": re.compile(r"\b[a-f0-9]{32,64}\b"),
    "IPV4": re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"),
}

# Prompt Injection & Adversarial Attack Heuristic Patterns
INJECTION_SIGNATURES: List[Pattern] = [
    re.compile(r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)", re.IGNORECASE),
    re.compile(r"(?i)disregard\s+(all\s+)?(previous|prior|above)\s+(instructions|directives)", re.IGNORECASE),
    re.compile(r"(?i)system\s*override", re.IGNORECASE),
    re.compile(r"(?i)you\s+are\s+now\s+(in\s+)?(developer\s+mode|dan\s+mode|unrestricted\s+mode)", re.IGNORECASE),
    re.compile(r"(?i)jailbreak", re.IGNORECASE),
    re.compile(r"(?i)reveal\s+(your\s+)?(system\s+prompt|hidden\s+instructions|master\s+prompt)", re.IGNORECASE),
    re.compile(r"(?i)print\s+(the\s+)?(system\s+prompt|initial\s+prompt)", re.IGNORECASE),
    re.compile(r"(?i)<\s*system\s*>", re.IGNORECASE),
    re.compile(r"(?i)\[\s*system\s*\]", re.IGNORECASE),
]
