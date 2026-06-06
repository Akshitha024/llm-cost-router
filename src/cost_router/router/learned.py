"""Learned router: a small logistic-regression classifier picks the provider.

Trains on a calibration set: (query features) -> (cheapest provider that
will get this query correct). At inference time, predicts that provider.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LogisticRegression  # type: ignore[import-untyped]

from cost_router.features.extract import feature_matrix, features
from cost_router.providers.registry import all_providers
from cost_router.types import Query, RouteOutcome


@dataclass
class LearnedRouter:
    clf: LogisticRegression
    provider_names: list[str]


def train(queries: list[Query], seed: int = 17) -> LearnedRouter:
    """Build a (features -> provider index) classifier on the calibration set."""
    rng = random.Random(seed)
    provs = all_providers()
    labels: list[int] = []
    for q in queries:
        chosen = -1
        for i, p in enumerate(provs):
            conf = p.accuracy_for(q.difficulty)
            if rng.random() < conf:
                chosen = i
                break
        if chosen == -1:
            chosen = len(provs) - 1  # default to most-capable
        labels.append(chosen)
    X = feature_matrix(queries)
    y = np.array(labels)
    if len(set(y)) < 2:
        # degenerate: only one class. Default to the cheapest as a fallback.
        y = np.array([0, *list(y[:-1])])
    clf = LogisticRegression(max_iter=500)
    clf.fit(X, y)
    return LearnedRouter(clf=clf, provider_names=[p.name for p in provs])


def route(queries: list[Query], router: LearnedRouter, seed: int = 19) -> list[RouteOutcome]:
    rng = random.Random(seed)
    provs = all_providers()
    by_name = {p.name: p for p in provs}
    outs: list[RouteOutcome] = []
    X = np.stack([features(q) for q in queries])
    preds = router.clf.predict(X)
    for q, idx in zip(queries, preds, strict=True):
        p = by_name[router.provider_names[int(idx)]]
        cost = p.cost_per_call_usd
        correct = rng.random() < p.accuracy_for(q.difficulty)
        outs.append(
            RouteOutcome(
                query_id=q.id, chosen=p.name, fallback_used=False, correct=correct, cost_usd=cost
            )
        )
    return outs
