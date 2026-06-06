"""Feature extraction for the learned router."""

from __future__ import annotations

import numpy as np

from cost_router.types import Query


def features(q: Query) -> np.ndarray:
    """Return a small float vector summarizing this query.

    The features are intentionally cheap to compute so the router itself
    is not a bottleneck.
    """
    return np.array(
        [
            float(q.prompt_length) / 1000.0,
            float(q.has_code),
            float(q.has_math),
        ],
        dtype=np.float64,
    )


def feature_matrix(queries: list[Query]) -> np.ndarray:
    return np.stack([features(q) for q in queries])
