"""Cascade router: try cheap first, escalate to mid, escalate to expensive.

The cascade decides whether to escalate based on a per-provider "confidence"
threshold; in the absence of true logits, we approximate confidence as the
provider's per-difficulty accuracy. When the simulated answer is wrong AND
the simulated confidence is below `escalation_threshold`, we escalate.
"""

from __future__ import annotations

import random

from cost_router.providers.registry import cheap, expensive, mid
from cost_router.types import Provider, Query, RouteOutcome


def route(
    queries: list[Query],
    escalation_threshold: float = 0.75,
    seed: int = 17,
) -> list[RouteOutcome]:
    rng = random.Random(seed)
    outs: list[RouteOutcome] = []
    cheap_p = cheap()
    mid_p = mid()
    exp_p = expensive()

    for q in queries:
        cost = 0.0
        used_models: list[Provider] = []

        for prov in [cheap_p, mid_p, exp_p]:
            used_models.append(prov)
            cost += prov.cost_per_call_usd
            conf = prov.accuracy_for(q.difficulty)
            correct = rng.random() < conf
            if conf >= escalation_threshold:
                outs.append(
                    RouteOutcome(
                        query_id=q.id,
                        chosen=prov.name,
                        fallback_used=len(used_models) > 1,
                        correct=correct,
                        cost_usd=cost,
                    )
                )
                break
        else:
            outs.append(
                RouteOutcome(
                    query_id=q.id,
                    chosen=used_models[-1].name,
                    fallback_used=True,
                    correct=False,
                    cost_usd=cost,
                )
            )
    return outs
