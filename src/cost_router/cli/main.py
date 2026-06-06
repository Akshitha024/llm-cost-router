"""Typer CLI for llm-cost-router."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from cost_router.runner import run

app = typer.Typer(no_args_is_help=True, help="Cost-aware LLM router benchmark.")
console = Console()


@app.command()
def bench(
    out_dir: Path = typer.Option(Path("runs/latest")),
    n: int = typer.Option(300),
    seed: int = typer.Option(17),
) -> None:
    """Run three routers (always-cheap, cascade, learned) and write summary.json + 5 PNGs."""
    res = run(out_dir, n=n, seed=seed)
    console.print_json(json.dumps(res["aggregate"], default=str))


@app.command()
def report(out_dir: Path = typer.Option(Path("runs/latest"))) -> None:
    """Pretty-print accuracy + cost by router."""
    data = json.loads((out_dir / "summary.json").read_text())
    table = Table(title="Routers")
    for col in ("router", "n", "accuracy", "total_usd"):
        table.add_column(col)
    for name, row in data["aggregate"].items():
        table.add_row(
            name,
            str(int(row["n"])),
            f"{row['accuracy']:.2%}",
            f"${row['total_usd']:.4f}",
        )
    console.print(table)


if __name__ == "__main__":
    app()
