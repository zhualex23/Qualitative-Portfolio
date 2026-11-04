import numpy as np
import pandas as pd
from .config import SECTORS, Config
from .data import returns_from_prices


def _equal():
    return pd.Series(1.0 / len(SECTORS), index=SECTORS, dtype=float)


def _rebalance_dates(index, frequency):
    periods = index.to_period(frequency)
    return set(index[~periods.duplicated()])


def _history(prices, date):
    return prices.loc[prices.index < date]


def single_index_fast_weights(est_returns):
    """EGP single-index analytical cutoff using daily excess returns.

    Closely follows the final working-draft algorithm. Excludes assets with
    nonpositive beta or nonpositive residual variance; equal-weight fallback.
    """
    if len(est_returns) < 200:
        return _equal()
    market = est_returns['SPY']-est_returns['BIL']
    rows = []
    for sector in SECTORS:
        aligned = pd.concat([est_returns[sector]-est_returns['BIL'],market],axis=1).dropna()
        if len(aligned) < 60:
            continue
        y,x = aligned.iloc[:,0].to_numpy(),aligned.iloc[:,1].to_numpy()
        mv = np.var(x,ddof=1)
        if not np.isfinite(mv) or mv <= 1e-12:
            continue
        beta = np.cov(y,x,ddof=1)[0,1]/mv
        alpha = y.mean()-beta*x.mean()
        residual_var = np.var(y-alpha-beta*x,ddof=1)
        if not np.isfinite(beta) or beta <= 1e-12 or not np.isfinite(residual_var) or residual_var <= 1e-12:
            continue
        excess = y.mean()
        rows.append((sector,beta,residual_var,excess,excess/beta))
    if not rows:
        return _equal()
    info = pd.DataFrame(rows,columns=['sector','beta','resid_var','excess','ratio']).sort_values('ratio',ascending=False).reset_index(drop=True)
    sigma_m2 = market.var(ddof=1)
    if not np.isfinite(sigma_m2) or sigma_m2 <= 1e-12:
        return _equal()
    a = (info['excess']*info['beta']/info['resid_var']).cumsum()
    b = (info['beta']**2/info['resid_var']).cumsum()
    cutoff = sigma_m2*a/(1+sigma_m2*b)
    eligible = np.flatnonzero((info['ratio'] > cutoff).to_numpy())
    if len(eligible) == 0:
        return _equal()
    k = eligible[-1]
    cstar = cutoff.iloc[k]
    active = info.iloc[:k+1].copy()
    z = active['beta']/active['resid_var']*(active['ratio']-cstar)
    z = z.clip(lower=0)
    if z.sum() <= 0:
        return _equal()
    weights = pd.Series(0.0,index=SECTORS)
    weights.loc[active['sector']] = (z/z.sum()).to_numpy()
    return weights / weights.sum()


def momentum_weights(history, config=Config()):
    """Draft implementation: 12-1 proxy / 60-day daily volatility, top 3 positive."""
    scores = {}
    for sector in SECTORS:
        series = history[sector].dropna()
        if len(series) < config.lookback+config.momentum_skip:
            continue
        # Match draft offsets exactly: end at t-21, begin at t-273.
        previous = series.iloc[-(config.momentum_skip+1)]
        old = series.iloc[-(config.lookback+config.momentum_skip)]
        raw_mom = previous / old - 1
        recent = history[sector].pct_change(fill_method=None).dropna().tail(config.vol_window)
        if len(recent) < config.vol_window:
            continue
        vol = recent.std(ddof=1)
        if np.isfinite(vol) and vol > 1e-12 and np.isfinite(raw_mom):
            scores[sector] = raw_mom / vol
    scores = pd.Series(scores,dtype=float)
    positive = scores[scores>0].sort_values(ascending=False).head(config.top_n)
    if positive.empty:
        return _equal()
    weights = pd.Series(0.,index=SECTORS)
    weights.loc[positive.index] = positive / positive.sum()
    return weights


def spy_buy_hold(returns, config=Config()):
    s = returns.loc[config.start:config.end,'SPY'].dropna()
    return s.rename('SPY Buy & Hold'),pd.DataFrame(columns=['Date',*SECTORS])


def balanced_6040(returns, config=Config()):
    """Quarterly target reset, otherwise drift; records pre-return weights."""
    daily = returns.loc[config.start:config.end,['SPY','BND']].dropna()
    dates = _rebalance_dates(daily.index,'Q')
    weights = np.array([0.6,0.4],dtype=float)
    out, records = [], []
    for date, row in daily.iterrows():
        if date in dates:
            weights = np.array([0.6,0.4])
        records.append({'Date':date,'SPY':weights[0],'BND':weights[1], 'rebalance':date in dates})
        r = row.to_numpy(dtype=float)
        out.append(np.dot(weights,r))
        gross = weights*(1+r)
        weights = gross/gross.sum()
    return pd.Series(out,index=daily.index,name='60/40 SPY-BND'),pd.DataFrame(records).set_index('Date')


def sector_strategy(prices,kind,config=Config()):
    """Signals use dates strictly prior to rebalance; fixed weights until next rebalance.

    This preserves the original draft's daily constant-weight calculation for
    sector strategies; unlike 60/40, it does not drift constituent weights.
    """
    returns = returns_from_prices(prices)
    bt = returns.loc[config.start:config.end]
    freq = 'Q' if kind == 'fast' else 'M'
    rebalance_dates = _rebalance_dates(bt.index,freq)
    current_weights = _equal() if kind=='fast' else pd.Series(0.,index=SECTORS)
    out, records = [], []
    for date in bt.index:
        if date in rebalance_dates:
            hist = _history(prices.loc['2018-01-01':],date)
            if kind == 'fast':
                est = returns_from_prices(hist).tail(config.lookback)
                est = est.dropna(subset=['SPY','BIL',*SECTORS])
                current_weights = single_index_fast_weights(est)
            elif kind == 'momentum':
                current_weights = momentum_weights(hist,config)
            else:
                raise ValueError('kind must be fast or momentum')
            records.append({'Date':date,**current_weights.to_dict()})
        day = bt.loc[date,list(SECTORS)]
        valid = day.notna() & (current_weights>0)
        if valid.sum()==0:
            p_return = 0.0
        else:
            valid_w = current_weights[valid]
            p_return = float(np.dot((valid_w/valid_w.sum()).to_numpy(),day[valid].to_numpy(dtype=float)))
        out.append(p_return)
    name = 'Single-Index Fast Algorithm' if kind=='fast' else 'Risk-Adjusted Momentum'
    return pd.Series(out,index=bt.index,name=name),pd.DataFrame(records).set_index('Date')


def run_all(prices,config=Config()):
    returns = returns_from_prices(prices)
    spy,_ = spy_buy_hold(returns,config)
    balanced,balanced_weights = balanced_6040(returns,config)
    fast,fast_weights = sector_strategy(prices,'fast',config)
    momentum,momentum_weights_history = sector_strategy(prices,'momentum',config)
    panel = pd.concat([spy,balanced,fast,momentum],axis=1)
    panel = panel.join(returns.loc[config.start:config.end,['BIL']].rename(columns={'BIL':'rf'}))
    panel = panel.dropna(subset=['SPY Buy & Hold','60/40 SPY-BND','rf'])
    return panel,{'balanced':balanced_weights,'fast':fast_weights,'momentum':momentum_weights_history}
