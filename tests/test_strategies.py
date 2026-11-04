import numpy as np
import pandas as pd
from quant_portfolio.config import SECTORS,Config
from quant_portfolio.strategies import momentum_weights,single_index_fast_weights,balanced_6040,run_all
from quant_portfolio.metrics import performance

def sample_prices(n=650):
    rng=np.random.default_rng(42)
    dates=pd.bdate_range('2017-01-02',periods=n)
    tickers=['SPY','BND','BIL',*SECTORS]
    data={k:100*np.cumprod(1+rng.normal(0.0003,0.008 if k!='BIL' else 0.00002,n)) for k in tickers}
    return pd.DataFrame(data,index=dates)

def test_momentum_weights_long_only_and_fully_invested():
    w=momentum_weights(sample_prices(),Config())
    assert (w>=0).all() and np.isclose(w.sum(),1)
    assert (w>0).sum()<=3 or (w>0).sum()==len(SECTORS)

def test_fast_weights_normalized():
    est=sample_prices().pct_change(fill_method=None).dropna().tail(252)
    w=single_index_fast_weights(est)
    assert (w>=0).all() and np.isclose(w.sum(),1)

def test_quarterly_balance():
    prices=sample_prices()
    returns=prices.pct_change(fill_method=None)
    series,weights=balanced_6040(returns,Config(start='2018-01-01',end='2019-06-30'))
    assert len(series)>0 and np.isclose(weights.iloc[0]['SPY'],0.6)
    assert np.allclose(weights.loc[weights['rebalance'],['SPY','BND']], [0.6,0.4])

def test_all_strategies_and_metrics():
    prices=sample_prices(900)
    cfg=Config(start='2019-01-01',end='2020-06-30')
    panel,weights=run_all(prices,cfg)
    assert len(panel)>20 and panel.shape[1]==5
    assert len(weights['momentum'])>0
    stats=performance(panel['SPY Buy & Hold'],panel['rf'],panel['SPY Buy & Hold'])
    assert np.isclose(stats['Beta vs SPY'],1)
    assert abs(stats['Jensen Alpha Annualized'])<1e-10
