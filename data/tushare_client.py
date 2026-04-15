"""Tushare wrapper: concepts, prices, financials — replaces Gangtise RAG."""
import tushare as ts
import pandas as pd
from functools import lru_cache
from config import TUSHARE_TOKEN

ts.set_token(TUSHARE_TOKEN)
_pro = ts.pro_api()


@lru_cache(maxsize=1)
def list_concepts() -> pd.DataFrame:
    """List all concept boards. Returns DataFrame with columns: code, name, src."""
    return _pro.concept(src="ts")


def find_concept(keyword: str) -> pd.DataFrame:
    """Fuzzy-match concepts by keyword in name."""
    df = list_concepts()
    return df[df["name"].str.contains(keyword, na=False)]


@lru_cache(maxsize=32)
def concept_stocks(concept_code: str) -> pd.DataFrame:
    """Get all stocks in a concept board.

    Returns columns: ts_code, name, concept_name, in_date, out_date
    """
    return _pro.concept_detail(id=concept_code)


@lru_cache(maxsize=1)
def stock_basic() -> pd.DataFrame:
    """Full A-share metadata: ts_code, name, industry, market, list_date."""
    return _pro.stock_basic(
        exchange="",
        list_status="L",
        fields="ts_code,name,area,industry,market,list_date"
    )


def daily_prices(ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Daily OHLCV for a single stock. Dates: YYYYMMDD."""
    return _pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)


def index_daily(ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Daily index prices (e.g., 000300.SH for CSI300)."""
    return _pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)


def fina_indicator(ts_code: str, period: str | None = None) -> pd.DataFrame:
    """Core financial indicators: ROE, margin, growth rates. period=YYYYMMDD."""
    return _pro.fina_indicator(ts_code=ts_code, period=period)


def enrich_stocks_with_industry(ts_codes: list[str]) -> pd.DataFrame:
    """Given a list of ts_codes, return a table with industry metadata."""
    basic = stock_basic()
    return basic[basic["ts_code"].isin(ts_codes)][["ts_code", "name", "industry", "market"]]
