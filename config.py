"""Config: load env vars and strategy parameters."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Strategy params (from Huatai report)
CHAIN_MIN_NODES = 4
CHAIN_MAX_NODES = 8
STOCKS_PER_NODE_MIN = 5
STOCKS_PER_NODE_MAX = 10
PORTFOLIO_MAX_SIZE = 30
BENCHMARK = "000300.SH"  # CSI 300
