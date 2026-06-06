"""Synthetic query dataset with controlled difficulty mix."""

from __future__ import annotations

import random

from cost_router.types import Difficulty, Query


def synthesize(n: int = 300, seed: int = 17) -> list[Query]:
    rng = random.Random(seed)
    qs: list[Query] = []
    for i in range(n):
        r = rng.random()
        if r < 0.5:
            d = Difficulty.EASY
        elif r < 0.8:
            d = Difficulty.MEDIUM
        else:
            d = Difficulty.HARD
        plen = int(rng.lognormvariate(6.0, 0.4))
        qs.append(
            Query(
                id=i,
                difficulty=d,
                prompt_length=plen,
                has_code=rng.random() < (0.15 if d == Difficulty.EASY else 0.4),
                has_math=rng.random() < (0.05 if d == Difficulty.EASY else 0.35),
            )
        )
    return qs
