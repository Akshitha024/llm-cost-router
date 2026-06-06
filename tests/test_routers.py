"""Tests for the cascade and learned routers."""

from __future__ import annotations

from cost_router.bench.dataset import synthesize
from cost_router.router.cascade import route as cascade_route
from cost_router.router.learned import route as learned_route
from cost_router.router.learned import train


def test_cascade_routes_every_query() -> None:
    qs = synthesize(n=20, seed=4)
    outs = cascade_route(qs)
    assert len(outs) == 20


def test_cascade_assigns_known_provider() -> None:
    qs = synthesize(n=20, seed=4)
    outs = cascade_route(qs)
    assert all(o.chosen in {"haiku-class", "sonnet-class", "opus-class"} for o in outs)


def test_learned_routes_every_query() -> None:
    qs = synthesize(n=60, seed=5)
    calib, test = qs[:20], qs[20:]
    router = train(calib)
    outs = learned_route(test, router)
    assert len(outs) == 40


def test_learned_uses_at_least_one_provider() -> None:
    qs = synthesize(n=60, seed=5)
    calib, test = qs[:20], qs[20:]
    router = train(calib)
    outs = learned_route(test, router)
    assert {o.chosen for o in outs}
