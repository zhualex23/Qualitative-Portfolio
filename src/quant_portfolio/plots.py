from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

def save_charts(panel,weights,destination):
    destination = Path(destination)
    destination.mkdir(parents=True,exist_ok=True)
    rets=panel.drop(columns='rf')
    nav=(1+rets).cumprod()
    drawdown=nav/nav.cummax()-1
    ax=nav.plot(figsize=(11,6),title='Cumulative NAV — 2019–2023',grid=True)
    ax.set_ylabel('NAV (initial = 1)')
    plt.tight_layout();plt.savefig(destination/'nav_comparison.png',dpi=160);plt.close()
    ax=drawdown.plot(figsize=(11,6),title='Drawdowns — 2019–2023',grid=True)
    ax.set_ylabel('Drawdown')
    plt.tight_layout();plt.savefig(destination/'drawdown_comparison.png',dpi=160);plt.close()
    for col in rets:
        slug=col.lower().replace(' ','_').replace('/','_').replace('&','and')
        fig,axes=plt.subplots(1,3,figsize=(16,4))
        nav[col].plot(ax=axes[0],title='NAV',grid=True)
        drawdown[col].plot(ax=axes[1],title='Drawdown',grid=True)
        rolling=nav[col].pct_change(252).resample('ME').last().dropna()
        axes[2].hist(rolling,bins=20)
        axes[2].set_title('Monthly sampled rolling 1-year returns')
        fig.suptitle(col);fig.tight_layout();fig.savefig(destination/f'{slug}.png',dpi=160);plt.close(fig)
    for key in ('fast','momentum'):
        if not weights[key].empty:
            ax=weights[key].plot(figsize=(12,5),title=f'{key.title()} — rebalance weights',grid=True)
            ax.set_ylabel('Portfolio weight')
            plt.tight_layout();plt.savefig(destination/f'{key}_weights.png',dpi=160);plt.close()
    if not weights['balanced'].empty:
        ax=weights['balanced'][['SPY','BND']].plot(figsize=(12,5),title='60/40 pre-return weight drift',grid=True)
        plt.tight_layout();plt.savefig(destination/'balanced_weight_drift.png',dpi=160);plt.close()
