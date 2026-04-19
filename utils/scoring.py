"""
utils/scoring.py
Core logic: weighted factor scoring and Probability of Win (PoW) calculation.

Logic:
  1. Each candidate has raw scores (1-10) per factor.
  2. Multiply each raw score by its analyst-defined weight → weighted score.
  3. Sum all weighted scores → total weighted score per candidate.
  4. Apply softmax-style normalization to convert scores into PoW percentages
     that sum to 100% across all candidates.
"""

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)

MATRIX_FACTORS = [
    "incumbency_effect",
    "party_strength",
    "past_work_record",
    "personal_base",
    "religious_caste_base",
    "digital_sentiment",
]

# Temperature controls how "winner-takes-all" vs "spread out" the PoW is.
# Lower = more decisive, higher = more even. 1.5 gives realistic spread.
SOFTMAX_TEMPERATURE = 1.5


def compute_scores(
    candidates: list[dict[str, Any]],
    weights: dict[str, float],
) -> dict[str, dict[str, float]]:
    """
    Compute per-factor weighted scores and total score for each candidate.

    Args:
        candidates: List of candidate dicts with factor scores (1-10)
        weights:    Dict mapping factor name → analyst weight (0.5-3.0)

    Returns:
        Dict of {candidate_name: {factor: weighted_score, ..., "total": float}}
    """
    results = {}

    for cand in candidates:
        name   = cand["name"]
        factor_scores: dict[str, float] = {}
        total = 0.0

        for factor in MATRIX_FACTORS:
            raw    = float(cand.get(factor, 5))
            weight = weights.get(factor, 1.0)
            ws     = raw * weight
            factor_scores[factor] = round(ws, 2)
            total += ws

        factor_scores["total"] = round(total, 2)
        results[name] = factor_scores
        logger.debug(f"[compute_scores] {name}: total={total:.2f}")

    return results


def _softmax(values: list[float], temperature: float = SOFTMAX_TEMPERATURE) -> list[float]:
    """
    Softmax with temperature scaling.
    Converts raw scores into probabilities that sum to 1.

    Args:
        values:      List of raw scores
        temperature: Controls sharpness — lower = more decisive

    Returns:
        List of probabilities (0-1) summing to 1.0
    """
    scaled = [v / temperature for v in values]
    max_v  = max(scaled)  # numerical stability
    exps   = [math.exp(v - max_v) for v in scaled]
    total  = sum(exps)
    return [e / total for e in exps]


def compute_pow(scores: dict[str, dict[str, float]]) -> dict[str, float]:
    """
    Compute Probability of Win (PoW) for each candidate using softmax normalization.

    Args:
        scores: Output from compute_scores()

    Returns:
        Dict of {candidate_name: pow_percentage (0-100)}
    """
    names  = list(scores.keys())
    totals = [scores[n]["total"] for n in names]

    probs = _softmax(totals)

    pow_map = {name: round(prob * 100, 2) for name, prob in zip(names, probs)}
    logger.info(f"[compute_pow] Results: {pow_map}")
    return pow_map
