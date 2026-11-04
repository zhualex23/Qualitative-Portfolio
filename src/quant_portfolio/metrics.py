import numpy as np
import pandas as pd

def performance(returns, rf, benchmark, periods=252):
    """Metrics exactly follow displayed working-draft formulas where possible."""
    aligned = pd.concat([returns.rename('p'),rf.rename('rf'),benchmark.rename('market')],axis=1).dropna()
    if len(aligned) < 2:
        raise ValueError('At least two aligned daily observations required')
    p,r,m = aligned['p'],aligned['rf'],aligned['market']
    nav = (1+p).cumprod()
    drawdown = nav/nav.cummax()-1
    ann_return = nav.iloc[-1]**(periods/len(nav))-1
    ann_vol = p.std(ddof=1)*np.sqrt(periods)
    excess = p-r
    market_excess = m-r
    beta = excess.cov(market_excess)/market_excess.var(ddof=1)
    alpha = (excess.mean()-beta*market_excess.mean())*periods
    active = p-m
    te = active.std(ddof=1)*np.sqrt(periods)
    q = p.quantile(0.05)
    downside = p[p<0]
    downvol = downside.std(ddof=1)*np.sqrt(periods)
    risk_free_ann=(1+r.mean())**periods-1
    return {
        'Start':str(aligned.index.min().date()), 'End':str(aligned.index.max().date()),
        'Trading Days':len(p),'Cumulative Return':nav.iloc[-1]-1,
        'Annualized Return':ann_return,'Annualized Volatility':ann_vol,
        'Risk-Free Annual Return':risk_free_ann,
        'Sharpe Ratio':excess.mean()/p.std(ddof=1)*np.sqrt(periods),
        'Sortino Ratio':(ann_return-risk_free_ann)/downvol if downvol>0 else np.nan,
        'Maximum Drawdown':drawdown.min(), 'Daily VaR 95%':q,
        'Daily CVaR 95%':p[p<=q].mean(), 'Beta vs SPY':beta,
        'Jensen Alpha Annualized':alpha, 'Tracking Error vs SPY':te,
        'Information Ratio vs SPY':(active.mean()/active.std(ddof=1)*np.sqrt(periods)) if te>0 else np.nan,
    }

def comparison_table(panel,periods=252):
    return pd.DataFrame({col:performance(panel[col],panel['rf'],panel['SPY Buy & Hold'],periods)
                         for col in panel.columns if col != 'rf'}).T
