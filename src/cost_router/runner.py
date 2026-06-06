"""End-to-end runner: dataset -> three routers -> 5 charts + summary.json.

Three routers are compared:

  - **always-cheap**: always pick the cheap provider (baseline).
  - **cascade**: try cheap, escalate to mid then expensive if confidence low.
  - **learned**: small logistic-regression classifier trained on a 30%
    calibration split.
"""

from __future__ import annotations

import json
from pathlib import Path

from cost_router.bench.dataset import synthesize
from cost_router.providers.registry import all_providers, cheap
from cost_router.router.cascade import route as cascade_route
from cost_router.router.learned import route as learned_route
from cost_router.router.learned import train
from cost_router.types import Query, RouteOutcome
from cost_router.viz.charts import (
    accuracy_by_difficulty,
    cost_distribution_box,
    pareto_cost_quality,
    per_provider_usage_stack,
    per_router_accuracy_bar,
)


def _always_cheap(queries: list[Query], seed: int = 17) -> list[RouteOutcome]:
    import random

    rng = random.Random(seed)
    p = cheap()
    return [
        RouteOutcome(
            query_id=q.id,
            chosen=p.name,
            fallback_used=False,
            correct=rng.random() < p.accuracy_for(q.difficulty),
            cost_usd=p.cost_per_call_usd,
        )
        for q in queries
    ]


def run(out_dir: Path, n: int = 300, seed: int = 17) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    figs = Path("results/figures")
    all_q = synthesize(n=n, seed=seed)
    calib, test = all_q[: int(0.3 * n)], all_q[int(0.3 * n) :]

    learned = train(calib, seed=seed)

    named = {
        "always-cheap": _always_cheap(test, seed=seed),
        "cascade": cascade_route(test, seed=seed),
        "learned": learned_route(test, learned, seed=seed),
    }
    diff_by_qid = {q.id: q.difficulty.value for q in test}

    pareto_cost_quality(named, figs / "pareto.png")
    per_router_accuracy_bar(named, figs / "accuracy.png")
    per_provider_usage_stack(named, figs / "provider_usage.png")
    cost_distribution_box(named, figs / "cost_distribution.png")
    accuracy_by_difficulty(named, diff_by_qid, figs / "accuracy_by_difficulty.png")

    agg: dict[str, dict[str, float]] = {}
    for name, rows in named.items():
        agg[name] = {
            "n": float(len(rows)),
            "accuracy": sum(r.correct for r in rows) / max(1, len(rows)),
            "total_usd": sum(r.cost_usd for r in rows),
        }

    summary: dict[str, object] = {
        "n_test": len(test),
        "providers": [p.model_dump() for p in all_providers()],
        "aggregate": agg,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    return summary
