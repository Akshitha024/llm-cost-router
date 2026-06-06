"""Tests for the synthetic dataset."""

from __future__ import annotations

from cost_router.bench.dataset import synthesize
from cost_router.types import Difficulty


def test_count() -> None:
    assert len(synthesize(n=40, seed=1)) == 40


def test_difficulty_mix_roughly_matches_target() -> None:
    qs = synthesize(n=500, seed=2)
    by_d = {d: 0 for d in Difficulty}
    for q in qs:
        by_d[q.difficulty] += 1
    # We seeded the mix to roughly 50/30/20.
    assert by_d[Difficulty.EASY] > by_d[Difficulty.MEDIUM] > by_d[Difficulty.HARD]


def test_seed_determinism() -> None:
    a = synthesize(n=20, seed=3)
    b = synthesize(n=20, seed=3)
    assert [q.model_dump() for q in a] == [q.model_dump() for q in b]
