"""Types for the cost router."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Provider(BaseModel):
    """A model provider with its per-call cost and per-difficulty accuracy."""

    name: str
    cost_per_call_usd: float = Field(..., ge=0)
    accuracy_easy: float = Field(..., ge=0, le=1)
    accuracy_medium: float = Field(..., ge=0, le=1)
    accuracy_hard: float = Field(..., ge=0, le=1)

    def accuracy_for(self, d: Difficulty) -> float:
        return {
            "easy": self.accuracy_easy,
            "medium": self.accuracy_medium,
            "hard": self.accuracy_hard,
        }[d.value]


class Query(BaseModel):
    """A single query with a known difficulty and an oracle correctness label
    per provider."""

    id: int
    difficulty: Difficulty
    prompt_length: int = Field(..., ge=1)
    has_code: bool = False
    has_math: bool = False


class RouteOutcome(BaseModel):
    query_id: int
    chosen: str
    fallback_used: bool
    correct: bool
    cost_usd: float
