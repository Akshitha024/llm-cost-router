"""Five chart families for llm-cost-router."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from cost_router.types import RouteOutcome


def _save(fig: Figure, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


def pareto_cost_quality(named: dict[str, list[RouteOutcome]], out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name, rows in named.items():
        x = sum(r.cost_usd for r in rows)
        y = sum(r.correct for r in rows) / max(1, len(rows))
        ax.scatter([x], [y], s=120, label=name)
        ax.annotate(name, (x, y), textcoords="offset points", xytext=(7, 5), fontsize=9)
    ax.set_xlabel("total USD")
    ax.set_ylabel("accuracy")
    ax.set_title("Cost vs accuracy (Pareto)")
    ax.grid(alpha=0.3)
    ax.legend()
    return _save(fig, out)


def per_router_accuracy_bar(named: dict[str, list[RouteOutcome]], out: Path) -> Path:
    names = list(named.keys())
    accs = [sum(r.correct for r in named[n]) / max(1, len(named[n])) for n in names]
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(names, accs, color="#3b6fa1")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("accuracy")
    ax.set_title("Accuracy by router strategy")
    for b, a in zip(bars, accs, strict=True):
        ax.text(b.get_x() + b.get_width() / 2, a + 0.02, f"{a:.0%}", ha="center", fontsize=9)
    return _save(fig, out)


def per_provider_usage_stack(named: dict[str, list[RouteOutcome]], out: Path) -> Path:
    routers = list(named.keys())
    providers = sorted({o.chosen for rows in named.values() for o in rows})
    counts = np.zeros((len(providers), len(routers)))
    for j, r in enumerate(routers):
        for i, p in enumerate(providers):
            counts[i, j] = sum(o.chosen == p for o in named[r])
    fig, ax = plt.subplots(figsize=(7, 4))
    bottom = np.zeros(len(routers))
    colors = plt.get_cmap("tab10")
    for i, p in enumerate(providers):
        ax.bar(routers, counts[i], bottom=bottom, label=p, color=colors(i))
        bottom += counts[i]
    ax.set_ylabel("queries routed to provider")
    ax.set_title("Provider usage by router")
    ax.legend()
    return _save(fig, out)


def cost_distribution_box(named: dict[str, list[RouteOutcome]], out: Path) -> Path:
    routers = list(named.keys())
    data = [[o.cost_usd for o in named[r]] for r in routers]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot(data, tick_labels=routers)
    ax.set_ylabel("per-query cost (USD)")
    ax.set_title("Per-query cost distribution")
    return _save(fig, out)


def accuracy_by_difficulty(
    named: dict[str, list[RouteOutcome]], difficulty_by_qid: dict[int, str], out: Path
) -> Path:
    """Per-(router, difficulty) accuracy bar chart."""
    fig, ax = plt.subplots(figsize=(7, 4))
    difficulties = ["easy", "medium", "hard"]
    routers = list(named.keys())
    x = np.arange(len(difficulties))
    w = 0.8 / max(1, len(routers))
    palette = plt.get_cmap("tab10")
    for i, r in enumerate(routers):
        accs: list[float] = []
        for d in difficulties:
            rows = [o for o in named[r] if difficulty_by_qid.get(o.query_id) == d]
            accs.append(sum(o.correct for o in rows) / max(1, len(rows)))
        ax.bar(x + i * w - w * (len(routers) - 1) / 2, accs, w, label=r, color=palette(i))
    ax.set_xticks(x)
    ax.set_xticklabels(difficulties)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("accuracy")
    ax.set_title("Accuracy by difficulty bucket")
    ax.legend()
    return _save(fig, out)
