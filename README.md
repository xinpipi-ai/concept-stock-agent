# Concept Stock Agent

A runnable multi-agent stock selection project for theme and concept investing.

This project recreates the "concept stock selection" idea from the Huatai research note 《大模型概念与宏观热点选股》 and turns it into a local Python workflow. You give it a concept such as `AI算力` or `AI芯片`, and it builds an investable stock basket with rationale plus a simple backtest.

## What It Does

- Takes a concept name as input
- Maps the concept to a Tushare concept board
- Breaks the theme into industry-chain nodes
- Lets multiple agents expand stock candidates in parallel
- Reviews evidence across nodes and builds a final portfolio
- Runs an equal-weight backtest against CSI 300

## Why This Project Is Interesting

- It is not just a prompt demo. The pipeline is executable end to end.
- The output is structured enough to inspect, reuse, and backtest.
- It turns a sell-side research idea into a local research tool.
- The system is simple enough to run, but modular enough to extend.

## Pipeline

```text
planner
  -> chain_analyzer
  -> node_expander (parallel by industry-chain node)
  -> evidence_reviewer
  -> portfolio_builder
```

## Stack

- `Python`
- `Tushare` for concept matching, constituents, and market data
- `DeepSeek` for agent reasoning
- Local JSON artifacts for reproducible outputs

## Repository Structure

```text
agents/      agent implementations for planning, expansion, review, and portfolio building
data/        Tushare + model clients
run.py       CLI entry point
graph.py     pipeline orchestration
backtest.py  equal-weight backtest utilities
config.py    model, token, and strategy parameters
```

## Setup

```bash
cd "/Users/xinwei/Desktop/my show/concept_stock_agent"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a local `.env` file:

```bash
TUSHARE_TOKEN=your_tushare_token
DEEPSEEK_API_KEY=your_deepseek_key
```

## Usage

```bash
# Basic usage: pass a concept name and auto-match a Tushare concept board
python run.py "AI算力"

# Provide a Tushare concept code directly
python run.py "AI算力" --concept-code TS0001

# Run the stock-selection pipeline only
python run.py "AI算力" --skip-backtest

# Customize the backtest window
python run.py "AI算力" --backtest-start 20250101 --backtest-end 20260414
```

## Output

Each run generates a JSON file under `outputs/` with:

- Planning result
- Industry-chain decomposition
- Stock ideas by node
- Review comments and final selection logic
- Final portfolio

The CLI also prints the selected basket and, unless skipped, a backtest summary.

## Configurable Parameters

Main knobs live in `config.py`:

- `CHAIN_MIN_NODES` / `CHAIN_MAX_NODES`: number of chain nodes
- `STOCKS_PER_NODE_MIN` / `STOCKS_PER_NODE_MAX`: candidates per node
- `PORTFOLIO_MAX_SIZE`: final portfolio cap
- `BENCHMARK`: backtest benchmark, default `000300.SH`
- `DEEPSEEK_MODEL`: reasoning model, default `deepseek-chat`

## Switching Model Providers

The project is currently configured for DeepSeek, but the client layer is simple enough to swap.

For example, you can point the model settings in `config.py` to a Claude-compatible endpoint:

```python
DEEPSEEK_BASE_URL = "https://api.anthropic.com/v1"
DEEPSEEK_MODEL = "claude-sonnet-4-6"
```

Then replace the API key in `.env`.

## Roadmap Ideas

- Add richer evaluation metrics beyond equal-weight backtests
- Save intermediate agent traces as separate artifacts
- Compare multiple concepts in batch mode
- Support alternative data sources beyond Tushare
