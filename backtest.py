"""Simple equal-weight backtest with CSI300 benchmark."""
import pandas as pd
import numpy as np
from data import tushare_client
from config import BENCHMARK


def backtest_equal_weight(
    ts_codes: list[str],
    start_date: str,
    end_date: str,
) -> dict:
    """Buy & hold equal-weight portfolio vs CSI300.

    Dates in YYYYMMDD. Returns dict with daily NAV, metrics.
    """
    if not ts_codes:
        raise ValueError("Empty portfolio")

    # Fetch daily prices for each stock
    frames = []
    missing = []
    for code in ts_codes:
        df = tushare_client.daily_prices(code, start_date, end_date)
        if df.empty:
            missing.append(code)
            continue
        df = df[["trade_date", "close"]].rename(columns={"close": code})
        frames.append(df.set_index("trade_date"))

    if not frames:
        raise RuntimeError("No price data for any stock in portfolio")

    prices = pd.concat(frames, axis=1).sort_index()
    prices = prices.ffill().dropna(how="all")

    # Equal-weight NAV: normalize each stock to 1.0 at start, then average
    norm = prices / prices.iloc[0]
    portfolio_nav = norm.mean(axis=1)

    # Benchmark
    bench = tushare_client.index_daily(BENCHMARK, start_date, end_date)
    bench = bench.sort_values("trade_date").set_index("trade_date")["close"]
    bench_nav = bench / bench.iloc[0]

    # Align on common dates
    common = portfolio_nav.index.intersection(bench_nav.index)
    portfolio_nav = portfolio_nav.loc[common]
    bench_nav = bench_nav.loc[common]

    # Metrics
    p_returns = portfolio_nav.pct_change().dropna()
    b_returns = bench_nav.pct_change().dropna()

    total_ret = portfolio_nav.iloc[-1] - 1
    bench_ret = bench_nav.iloc[-1] - 1
    excess = total_ret - bench_ret

    ann_vol = p_returns.std() * np.sqrt(252)
    sharpe = (p_returns.mean() * 252) / ann_vol if ann_vol > 0 else 0

    # Max drawdown
    cummax = portfolio_nav.cummax()
    dd = (portfolio_nav - cummax) / cummax
    max_dd = dd.min()

    return {
        "portfolio_nav": portfolio_nav,
        "benchmark_nav": bench_nav,
        "metrics": {
            "total_return": float(total_ret),
            "benchmark_return": float(bench_ret),
            "excess_return": float(excess),
            "annualized_vol": float(ann_vol),
            "sharpe": float(sharpe),
            "max_drawdown": float(max_dd),
            "n_stocks": len(ts_codes) - len(missing),
            "missing_data": missing,
        },
    }


def print_backtest_report(result: dict):
    m = result["metrics"]
    print("\n" + "=" * 50)
    print("📈 Backtest Report")
    print("=" * 50)
    print(f"Stocks in backtest:   {m['n_stocks']}")
    if m["missing_data"]:
        print(f"Missing data:         {m['missing_data']}")
    print(f"Portfolio return:     {m['total_return']:+.2%}")
    print(f"Benchmark (CSI300):   {m['benchmark_return']:+.2%}")
    print(f"Excess return:        {m['excess_return']:+.2%}")
    print(f"Annualized vol:       {m['annualized_vol']:.2%}")
    print(f"Sharpe ratio:         {m['sharpe']:.2f}")
    print(f"Max drawdown:         {m['max_drawdown']:.2%}")
    print("=" * 50)
