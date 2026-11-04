from dataclasses import dataclass
SECTORS = ('XLC','XLY','XLP','XLE','XLF','XLV','XLI','XLB','XLRE','XLU','XLK')
REQUIRED = ('SPY','BND','BIL',*SECTORS)
@dataclass(frozen=True)
class Config:
    start: str = '2019-01-01'
    end: str = '2023-12-31'
    lookback: int = 252
    momentum_skip: int = 21
    vol_window: int = 60
    top_n: int = 3
    annualization: int = 252
