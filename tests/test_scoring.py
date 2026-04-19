"""
tests/test_scoring.py
Unit tests for scoring engine and candidate validator.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from utils.scoring import compute_scores, compute_pow, _softmax
from utils.validators import validate_candidate


MOCK_WEIGHTS = {
    "incumbency_effect":    1.0,
    "party_strength":       1.0,
    "past_work_record":     1.0,
    "personal_base":        1.0,
    "religious_caste_base": 1.0,
    "digital_sentiment":    1.0,
}

MOCK_CANDIDATES = [
    {
        "name": "Candidate A", "party": "Party X", "type": "Incumbent",
        "incumbency_effect": 7, "party_strength": 8, "past_work_record": 6,
        "personal_base": 7, "religious_caste_base": 5, "digital_sentiment": 6,
    },
    {
        "name": "Candidate B", "party": "Party Y", "type": "Challenger",
        "incumbency_effect": 0, "party_strength": 9, "past_work_record": 8,
        "personal_base": 8, "religious_caste_base": 7, "digital_sentiment": 9,
    },
]


# ── compute_scores ────────────────────────────────────────────────────────────

def test_compute_scores_returns_all_candidates():
    scores = compute_scores(MOCK_CANDIDATES, MOCK_WEIGHTS)
    assert "Candidate A" in scores
    assert "Candidate B" in scores


def test_compute_scores_total_correct():
    scores = compute_scores(MOCK_CANDIDATES, MOCK_WEIGHTS)
    # Candidate A: 7+8+6+7+5+6 = 39
    assert scores["Candidate A"]["total"] == pytest.approx(39.0)


def test_compute_scores_weighted_correctly():
    weights = {**MOCK_WEIGHTS, "party_strength": 2.0}
    scores  = compute_scores(MOCK_CANDIDATES, weights)
    # Candidate A party_strength: 8 * 2.0 = 16.0
    assert scores["Candidate A"]["party_strength"] == pytest.approx(16.0)


# ── compute_pow ───────────────────────────────────────────────────────────────

def test_pow_sums_to_100():
    scores = compute_scores(MOCK_CANDIDATES, MOCK_WEIGHTS)
    pow    = compute_pow(scores)
    total  = sum(pow.values())
    assert abs(total - 100.0) < 0.1


def test_pow_higher_score_wins():
    scores = compute_scores(MOCK_CANDIDATES, MOCK_WEIGHTS)
    pow    = compute_pow(scores)
    # Candidate B has higher total, should have higher PoW
    assert pow["Candidate B"] > pow["Candidate A"]


def test_pow_all_positive():
    scores = compute_scores(MOCK_CANDIDATES, MOCK_WEIGHTS)
    pow    = compute_pow(scores)
    assert all(v > 0 for v in pow.values())


# ── softmax ───────────────────────────────────────────────────────────────────

def test_softmax_sums_to_one():
    result = _softmax([10.0, 20.0, 30.0])
    assert abs(sum(result) - 1.0) < 1e-6


def test_softmax_highest_value_wins():
    result = _softmax([5.0, 10.0, 3.0])
    assert result[1] == max(result)


# ── validate_candidate ────────────────────────────────────────────────────────

def test_valid_candidate_passes():
    cand = {**MOCK_CANDIDATES[0]}
    valid, msg = validate_candidate(cand)
    assert valid is True


def test_empty_name_fails():
    cand = {**MOCK_CANDIDATES[0], "name": ""}
    valid, msg = validate_candidate(cand)
    assert valid is False
    assert "name" in msg.lower()


def test_empty_party_fails():
    cand = {**MOCK_CANDIDATES[0], "party": ""}
    valid, msg = validate_candidate(cand)
    assert valid is False


def test_out_of_range_score_fails():
    cand = {**MOCK_CANDIDATES[0], "party_strength": 15}
    valid, msg = validate_candidate(cand)
    assert valid is False
    assert "party_strength" in msg
