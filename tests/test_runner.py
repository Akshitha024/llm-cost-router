"""End-to-end runner smoke test."""

from __future__ import annotations

from pathlib import Path

from cost_router.runner import run


def test_runner_smoke(tmp_path: Path) -> None:
    res = run(tmp_path / "out", n=80, seed=1)
    assert res["n_test"] > 0
    assert (tmp_path / "out" / "summary.json").exists()
    agg = res["aggregate"]
    assert isinstance(agg, dict)
    for name in ("always-cheap", "cascade", "learned"):
        assert name in agg  # type: ignore[operator]
