# Replication checklist

1. Use course-provided adjusted-price `Data File.csv`, not a simulated or web-scraped substitute.
2. Run `python -m pip install -e ".[dev]"`.
3. Run `python -m pytest -q`.
4. Run `qp-backtest --data 'data/Data File.csv'`.
5. Compare `results/generated/metrics.csv` to `results/presentation_reference_metrics.csv`.
6. Examine any discrepancy using window selection, ticker inception availability, complete-case handling, and intraquarter weight conventions.

**Verification completed, November 2026:** The original course Excel workbook was supplied and converted to `data/Data File.csv` (4,529 dated observations; 25 columns including Date). The reconstructed pipeline generated `results/verified_metrics_original_course_data.csv`, and detailed differences are in `results/verification_comparison.csv`. Presentation values match at displayed two-decimal precision for return, Sharpe and drawdown. At higher precision the 60/40 annualized return is 0.100212 versus the reference 0.100217 (a difference of approximately 0.000005 in decimal return); this may reflect an implementation detail concerning first-day weight drift. Reference historical numbers should not be silently substituted for computed results.
