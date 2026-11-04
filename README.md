# Quantitative Portfolio Project

**Johns Hopkins University · 553.647 Quantitative Portfolio Theory & Performance Analysis · Spring 2026 · Group 3**

A GitHub-ready, research-focused Python recreation of the project's four ETF strategies, backtest workflow, performance metrics, weight histories, and charts. The strategy mechanics are reconstructed from the final presentation, the executed project draft, and the RFP response.

## Historical results reported in the final presentation

| Strategy | Annualized return | Annualized volatility | Sharpe | Max drawdown |
|---|---:|---:|---:|---:|
| SPY buy-and-hold | 15.62% | 20.99% | 0.72 | -33.72% |
| 60/40 SPY/BND | 10.02% | 13.15% | 0.66 | -21.03% |
| Single-index Fast Algorithm | 17.29% | 23.52% | 0.72 | -32.81% |
| Risk-adjusted momentum | 18.04% | 22.35% | 0.78 | -30.32% |

These historical figures have now been **independently recalculated using the original course Excel dataset** and match the displayed presentation precision. See `results/verified_metrics_original_course_data.csv` and `results/verification_comparison.csv` for detailed verification. The reported metrics are retained in `results/presentation_reference_metrics.csv`. Small higher-precision differences occur for the 60/40 model; see `docs/REPRODUCIBILITY.md`.

## Quick start

1. Install Python 3.10+ and dependencies:

   ```bash
   python -m pip install -e ".[dev]"
   ```

2. Use the original course-provided adjusted-close CSV, `data/Data File.csv`. It is included in the **local reproduction package**, but intentionally excluded from the **public GitHub package** and Git tracking pending permission to redistribute course data. A column guide is in `data/README.md`.

3. Run the full backtest:

   ```bash
   qp-backtest --data "data/Data File.csv" --out results/generated
   ```

   Or: `python -m quant_portfolio.cli --data "data/Data File.csv"`

4. Run tests: `python -m pytest -q`

Generated deliverables include per-day return series, comparative metrics, the three portfolio weight-history CSVs, NAV charts, drawdowns, and sampled rolling 1-year return histograms.

## Methods

- **Universe:** 11 SPDR sector ETFs: XLC, XLY, XLP, XLE, XLF, XLV, XLI, XLB, XLRE, XLU, XLK.
- **Market and cash proxies:** SPY; BIL daily adjusted-price returns.
- **Backtest:** January 2019–December 2023; historical estimates use pre-rebalance observations.
- **Task 1:** 100% SPY buy-and-hold.
- **Task 2:** 60% SPY / 40% BND; quarterly rebalance, weights drift intraquarter.
- **Task 3:** Elton–Gruber–Padberg single-index Fast Algorithm, 252-day trailing return estimates, positive-beta asset eligibility, analytical cutoff and long-only normalized weights, quarterly allocation.
- **Task 4:** monthly risk-adjusted momentum rotation: sector return through the point 21 trading sessions before rebalance over a preceding ~252-session lookback; divide by trailing 60-day daily volatility; keep up to three positive-scoring sectors and weight proportional to scores.
- **Metrics:** annualized CAGR, volatility, Sharpe, Sortino, maximum drawdown, daily historical 95% VaR/CVaR, market beta, Jensen alpha, tracking error and information ratio.

Full implementation decisions and known divergences: [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).

## Repository map

```text
src/quant_portfolio/     Portfolio engine, analytics, figures and CLI
scripts/                 Alternative entry-point
notebooks/               Guided analysis notebook
results/                 Reference historical metrics (recomputed results generated locally)
data/                    Expected input CSV schema; source CSV not distributed
tests/                   Automated unit and integration tests
docs/                    Methods, reproducibility notes and original source files
.github/workflows/       CI tests on pushes and pull requests
```

## Important reproducibility note

The **original market-data Excel file was subsequently supplied** and converted to `data/Data File.csv` without downloading substitute prices. All four strategies have been rerun on this data, and the original presentation metrics agree to displayed precision, with very small additional-decimal differences in 60/40. The GitHub package omits the raw course data to avoid publishing course-distributed materials without permission; the local package includes it. There are material methodology differences between the original *proposal* and the final *executed draft*; see methodology documentation. This is research/education, not trading advice.
