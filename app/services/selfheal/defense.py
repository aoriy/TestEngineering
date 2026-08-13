"""Three-layer anti-misjudgment defense (ADR-0005 / smart note #7).

Layer 1: verification — try the candidate locator in a real browser (Playwright);
        must be unique + visible + clickable. Injected as a callback by the UI
        executor (not available in the API-only slice yet).
Layer 2: semantic fingerprint — compare old/new element innerText/aria-label/role.
Layer 3: confidence gate — LLM confidence must be >= threshold else degrade to suggest.
"""

import difflib
from typing import Callable

from app.services.selfheal.llm import HealCandidate

VerifyFn = Callable[[HealCandidate], tuple[bool, str]]

CONFIDENCE_THRESHOLD = 0.8
SIMILARITY_THRESHOLD = 0.6


def semantic_similarity(old_meta: dict, candidate: HealCandidate) -> float:
    """Fingerprint similarity between the original element and a candidate."""
    if not old_meta:
        return 1.0

    def ratio(a: str, b: str) -> float:
        a, b = (a or "").strip(), (b or "").strip()
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

    role_match = 1.0 if old_meta.get("role") == candidate.role else 0.0
    text_sim = ratio(old_meta.get("inner_text", ""), candidate.inner_text)
    aria_sim = ratio(old_meta.get("aria_label", ""), candidate.aria_label)
    return 0.3 * role_match + 0.4 * text_sim + 0.3 * aria_sim


def evaluate(
    candidate: HealCandidate,
    confidence: float,
    old_meta: dict | None = None,
    verify: VerifyFn | None = None,
) -> tuple[bool, str]:
    """Return (passed, reason) for a candidate against the three layers."""
    if confidence < CONFIDENCE_THRESHOLD:
        return False, f"confidence {confidence:.2f} < {CONFIDENCE_THRESHOLD}"

    if verify is not None:
        ok, reason = verify(candidate)
        if not ok:
            return False, f"verification failed: {reason}"

    sim = semantic_similarity(old_meta or {}, candidate)
    if sim < SIMILARITY_THRESHOLD:
        return False, f"semantic similarity {sim:.2f} < {SIMILARITY_THRESHOLD}"

    return True, f"similarity {sim:.2f}"
