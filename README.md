# llm-cost-router
<p align="center">
  <img src="./results/figures/_hero.png" alt="llm-cost-router hero" width="100%"/>
</p>

<p align="center">
  <img alt="tests" src="https://img.shields.io/badge/tests-green-brightgreen?style=for-the-badge">
  <img alt="mypy" src="https://img.shields.io/badge/mypy-strict-blue?style=for-the-badge">
  <img alt="lint" src="https://img.shields.io/badge/ruff-clean-orange?style=for-the-badge">
  <img alt="pdf" src="https://img.shields.io/badge/research-15--page%20pdf-purple?style=for-the-badge">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-lightgrey?style=for-the-badge">
</p>

> ****



> Multi-provider LLM router with cascade-of-cheap-then-expensive and a small learned classifier; reports the cost vs accuracy Pareto across three router strategies.
> Last updated: 2024-08-15.

`llm-cost-router` benchmarks three router strategies on a synthetic mixed-difficulty query stream:

1. **always-cheap** baseline.
2. **cascade** that tries the cheap provider first and escalates if the per-call confidence falls below a threshold.
3. **learned** classifier (logistic regression on a 3-feature vector) trained on a 30% calibration split.

The headline output is a Pareto chart that places each router at a single (cost, accuracy) point so the operator can read off the dominant strategy at the operating point they care about.

## Headline (300-query fixture, seed=17)

| router | accuracy | total USD | per-query USD |
|---|---|---|---|
| always-cheap | ~80% | lowest | ~$0.0002 |
| cascade | ~90% | highest (escalates) | ~$0.005-0.015 |
| learned | ~88% | mid (model-picked) | between the two |

Reproduce: `make install && make bench && make report`.

## Pipeline

```mermaid
flowchart LR
  A[Synthetic query stream] --> B["Calibration split (30%)"]
  A --> C["Test split (70%)"]
  B --> D[Train logistic-regression learned router]
  C --> E[Run 3 routers]
  D --> E
  E --> F[5 chart families + summary.json]
```

## Five chart families

- `results/figures/pareto.png` - cost vs accuracy Pareto with router labels
- `results/figures/accuracy.png` - per-router accuracy bar
- `results/figures/provider_usage.png` - which provider each router picks (stacked bar)
- `results/figures/cost_distribution.png` - per-query cost boxplot
- `results/figures/accuracy_by_difficulty.png` - per-(router, difficulty) accuracy

## Repo layout

```
src/cost_router/
  types.py                  # Provider, Query, RouteOutcome
  providers/registry.py     # cheap / mid / expensive
  bench/dataset.py          # 300-query difficulty-mixed fixture
  router/
    cascade.py              # try cheap -> escalate
    learned.py              # logistic regression on features
  features/extract.py
  viz/charts.py
  cli/main.py               # `costrouter bench`, `costrouter report`
  runner.py
tests/                      # 8 tests, all green
docs/research_report.pdf    # rendered 15-page report
docs/_report/, docs/test_results/, results/figures/
CITATION.cff, LICENSE, Makefile, .github/workflows/ci.yml
```

## Quick start

```bash
make install   # uv sync --extra dev
make test      # pytest + mypy --strict + ruff
make bench     # run all 3 routers; write summary.json + 5 PNGs
make report    # pretty-print accuracy + cost
make pdf       # render docs/research_report.pdf
```

## Documentation

Long-form research report: [`docs/research_report.pdf`](./docs/research_report.pdf) (rendered) and [`docs/_report/research_report.md`](./docs/_report/research_report.md) (markdown source). Regenerate the PDF with `make pdf` (requires `pandoc` + `xelatex`).

Test artifacts (captured locally):

- [`docs/test_results/pytest_output.txt`](./docs/test_results/pytest_output.txt)
- [`docs/test_results/quality_gates.txt`](./docs/test_results/quality_gates.txt)
- [`docs/test_results/coverage_summary.txt`](./docs/test_results/coverage_summary.txt)

## References

- Chen, M., Chow, F., et al. "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance" (2023).
- Ong, R., et al. "RouteLLM: Learning to Route LLMs with Preference Data" (2024).

## License

MIT.

## Architecture

```mermaid
flowchart LR
    classDef io fill:#D90368,stroke:#1c1c1c,stroke-width:1.5px,color:#fff
    classDef proc fill:#2E294E,stroke:#1c1c1c,stroke-width:1.5px,color:#fff
    classDef out fill:#F1E9DA,stroke:#1c1c1c,stroke-width:1.5px,color:#fff
    A["📥 Inputs<br/>fixtures + configs"]:::io --> B["⚙️ Core pipeline<br/>llm"]:::proc
    B --> C["🧪 Evaluation<br/>5 chart families"]:::proc
    C --> D["📊 Artifacts<br/>summary.json + PNGs"]:::out
    C --> E["📄 PDF report<br/>15 pages"]:::out
```

## Pipeline sequence

```mermaid
sequenceDiagram
    autonumber
    participant U as User / CI
    participant M as Makefile
    participant R as Runner
    participant V as Viz
    participant P as PDF
    U->>M: make bench
    M->>R: invoke runner with seeded config
    R-->>R: load fixture + execute task
    R->>V: emit per-(metric, slice) records
    V-->>V: render 5 distinct chart families
    V->>U: write summary.json + PNG artifacts
    U->>M: make pdf
    M->>P: pandoc + xelatex
    P->>U: docs/research_report.pdf
```

## Concept mindmap

```mermaid
mindmap
  root((llm))
    Inputs
      Fixture
      Seed
      Config
    Core
      Modules
      Tests
      Mypy strict
    Outputs
      5 chart families
      summary json
      15-page PDF
    Quality
      Ruff
      Coverage
      CI on push
```


## Results gallery

<table>
  <tr>
    <td align="center"><strong>Pytest panel</strong><br/><img src="./docs/test_results/pytest_panel.png" width="100%"/></td>
    <td align="center"><strong>Coverage donut</strong><br/><img src="./docs/test_results/coverage_donut.png" width="100%"/></td>
  </tr>
  <tr>
    <td align="center"><strong>Quality gates</strong><br/><img src="./docs/test_results/quality_gates.png" width="100%"/></td>
    <td align="center"><strong>Headline metrics</strong><br/><img src="./docs/test_results/metrics_card.png" width="100%"/></td>
  </tr>
</table>

### Result charts (5 distinct families, palette: *Toll Plaza*)

<table>
  <tr><td align="center"><strong>Accuracy</strong><br/><img src="./results/figures/accuracy.png" width="100%"/></td><td align="center"><strong>Accuracy By Difficulty</strong><br/><img src="./results/figures/accuracy_by_difficulty.png" width="100%"/></td></tr>
  <tr><td align="center"><strong>Cost Distribution</strong><br/><img src="./results/figures/cost_distribution.png" width="100%"/></td><td align="center"><strong>Pareto</strong><br/><img src="./results/figures/pareto.png" width="100%"/></td></tr>
  <tr><td align="center"><strong>Provider Usage</strong><br/><img src="./results/figures/provider_usage.png" width="100%"/></td><td></td></tr>
</table>

