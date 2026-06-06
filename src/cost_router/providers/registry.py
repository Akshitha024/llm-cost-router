"""Canonical provider profiles."""

from __future__ import annotations

from cost_router.types import Provider


def cheap() -> Provider:
    return Provider(
        name="haiku-class",
        cost_per_call_usd=0.0002,
        accuracy_easy=0.95,
        accuracy_medium=0.78,
        accuracy_hard=0.42,
    )


def mid() -> Provider:
    return Provider(
        name="sonnet-class",
        cost_per_call_usd=0.0030,
        accuracy_easy=0.97,
        accuracy_medium=0.88,
        accuracy_hard=0.68,
    )


def expensive() -> Provider:
    return Provider(
        name="opus-class",
        cost_per_call_usd=0.0150,
        accuracy_easy=0.99,
        accuracy_medium=0.93,
        accuracy_hard=0.82,
    )


def all_providers() -> list[Provider]:
    return [cheap(), mid(), expensive()]
