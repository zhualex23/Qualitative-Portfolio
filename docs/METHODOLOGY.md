# Methods and reconstruction choices

## Evidence hierarchy
1. **Executed project draft (April 5, 2026):** source of detailed implementation of Task 3 and 4 and performance calculations.
2. **Final presentation (April 2026):** source of reported final performance and interpretation.
3. **RFP final (March 29, 2026):** mandate, ETF universe, proposal and evaluation criteria.

The documents are included unmodified under `docs/source_materials/`.

## Workflow

Input adjusted-close ETF prices → compute daily percent returns → filter 2019–2023 backtest → construct four daily return streams → compute compound NAV, annualized return/volatility and downside/risk-adjusted statistics → produce monthly sampled 252-session rolling return histograms and rebalance weights → cross-strategy comparison.

## Single-index fast strategy

At each quarter's first trading date use only preceding prices. Estimate a maximum 252-day return sample; consistent with the draft, require at least 200 complete observations across all sectors for fitting, otherwise use an equal-weight allocation. For each sector estimate beta against the SPY-minus-BIL excess return, intercept, regression residual variance, mean excess return. Sort by the mean-excess-return/beta ratio. Using cumulative A and B terms compute C_k = sigma_market^2 A_k / (1 + sigma_market^2 B_k). Take the final eligible k where ratio > C_k. Allocate weights proportional to (beta/residual_variance) × (ratio − C*), normalized, zero for excluded sectors. The code does not use SLSQP.

## Risk-adjusted momentum strategy

The RFP proposed simple 12–1 momentum, proportional positive-score weights. The **final working draft differs**: it divides each 12–1 return by the prior 60-session daily volatility, selects the **top three** positive signals, then weights proportionally. The production reconstruction follows the working draft. In early periods without sufficient estimation history, or when all scores are nonpositive, the draft uses **equal weighting**. At each month's first trading date, prices strictly earlier than the trading day determine the weights, preventing signal lookahead.

## Returns between rebalances

The draft's 60/40 strategy explicitly allows SPY/BND weights to drift every day and resets at quarterly dates. The draft's Fast Algorithm and momentum portfolio calculations use **fixed weights** through the holding period (daily reweighted sector exposures); the reconstructed code retains that distinction. This is **not** a true self-financing passive drift holding rule for those sector strategies and may affect transaction cost assumptions. No costs, fees, market impact, leverage, or slippage are applied.

## Metric definitions

- NAV = cumulative product of (1 + daily portfolio return).
- Annualized geometric return = final NAV^(252/N) − 1.
- Annualized volatility = sample standard deviation of daily returns × sqrt(252).
- Sharpe = mean(portfolio daily return − BIL daily return) / sample std(portfolio daily return) × sqrt(252).
- Sortino = (annualized portfolio return − annualized BIL mean-return proxy) / sample std(negative portfolio daily returns) × sqrt(252), following draft convention (not a target-zero semideviation convention).
- Daily VaR 95% = fifth percentile of returns; CVaR = mean returns at or below it.
- Beta = covariance(portfolio excess, SPY excess) / variance(SPY excess).
- Jensen alpha = 252 × [mean(portfolio excess) − beta × mean(SPY excess)].
- Tracking error = std(portfolio daily returns − SPY daily returns) × sqrt(252).
- Information ratio = annualized mean active return divided by annualized standard deviation of active returns.
- Rolling distribution = 252-day NAV percent changes, sampled at each calendar month-end.

## Potential original-source issues / audit considerations

1. **Missing source prices:** original adjusted close matrix is not included in the supplied files. No point estimate should be labeled independently reproduced without it.
2. **Different Task 3 descriptions:** RFP says covariance-matrix optimization/SciPy SLSQP; presentation and executed draft instead implement the analytical Elton–Gruber–Padberg Single-Index Fast Algorithm. We follow the latter.
3. **Different Task 4 descriptions:** RFP describes proportional raw positive momentum across sectors, while executed draft implements volatility-adjusted top-three ranking.
4. **Early estimation:** draft limits the data frame to dates since 2018 for Fast and Momentum. It therefore uses fallback equal weights early in 2019, despite earlier raw price history being present. **This repository mirrors the draft by limiting sector-signal history to 2018 onward**, even if earlier raw price history exists. Exact agreement still depends on the missing original course CSV.
5. **Constituent availability:** XLC and XLRE historical missingness makes complete-case estimation sensitive to listing dates; strict dropna affects the first fast-allocation dates. The draft's sample has these missing observations.
6. **First-day 60/40 weight bookkeeping:** the draft records the first day's pre-drift 60/40 weights and later post-drift weights. This reconstruction uniformly records pre-return weights (consistent economically, but not identical in column display).
7. **Strategy interpretation is contingent:** no transaction fees or out-of-sample robustness are established by the documents.

## Attribution

Course: Johns Hopkins University, 553.647, Spring 2026; Group 3. Source documents remain in the repository for traceability; project credit should be given to the whole team rather than only the uploader.
