import argparse
from pathlib import Path
from .config import Config
from .data import load_prices
from .strategies import run_all
from .metrics import comparison_table
from .plots import save_charts

def main():
    parser=argparse.ArgumentParser(description='Recreate the JHU Group 3 quantitative portfolio backtest')
    parser.add_argument('--data',required=True,help='Path to course-provided adjusted close CSV')
    parser.add_argument('--out',default='results/generated',help='Folder for backtest results')
    parser.add_argument('--start',default='2019-01-01')
    parser.add_argument('--end',default='2023-12-31')
    args=parser.parse_args()
    prices=load_prices(args.data)
    cfg=Config(start=args.start,end=args.end)
    panel,weights=run_all(prices,cfg)
    output=Path(args.out);output.mkdir(parents=True,exist_ok=True)
    panel.to_csv(output/'daily_returns.csv',index_label='Date')
    comparison=comparison_table(panel,cfg.annualization)
    comparison.to_csv(output/'metrics.csv',index_label='Strategy')
    for label,frame in weights.items():frame.to_csv(output/f'{label}_weights.csv',index_label='Date')
    save_charts(panel,weights,output/'charts')
    print(comparison.round(4).to_string())
    print('Saved outputs to',output.resolve())
if __name__=='__main__':main()
