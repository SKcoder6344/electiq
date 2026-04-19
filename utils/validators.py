"""
utils/validators.py
Validates candidate input before it enters the scoring pipeline.
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)

MATRIX_FACTORS = [
    "incumbency_effect",
    "party_strength",
    "past_work_record",
    "personal_base",
    "religious_caste_base",
    "digital_sentiment",
]

SCORE_RANGE = (0, 10)


def validate_candidate(candidate: dict) -> Tuple[bool, str]:
    """
    Validate a candidate dict before adding to session state.

    Args:
        candidate: Dict with name, party, type, and factor scores

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    name  = candidate.get("name", "").strip()
    party = candidate.get("party", "").strip()

    if not name:
        return False, "Candidate name cannot be empty."

    if len(name) < 2:
        return False, "Candidate name must be at least 2 characters."

    if not party:
        return False, "Party name cannot be empty."

    for factor in MATRIX_FACTORS:
        val = candidate.get(factor)
        if val is None:
            return False, f"Missing score for factor: {factor}"
        try:
            fval = float(val)
        except (TypeError, ValueError):
            return False, f"Score for '{factor}' must be a number."
        if not (SCORE_RANGE[0] <= fval <= SCORE_RANGE[1]):
            return False, f"Score for '{factor}' must be between {SCORE_RANGE[0]} and {SCORE_RANGE[1]}."

    logger.info(f"[validate_candidate] '{name}' passed validation")
    return True, "OK"
