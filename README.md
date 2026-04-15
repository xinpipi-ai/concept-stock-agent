# Concept Stock Agent

基于华泰金工研报《大模型概念与宏观热点选股》的多智能体概念选股复现。

## 架构

```
planner → chain_analyzer → node_expander (并行) → evidence_reviewer → portfolio_builder
```

- **数据源**: Tushare（替代报告中的 Gangtise RAG）
- **大模型**: DeepSeek（先便宜跑通，后续可切 Claude）
- **输出**: 月度概念股组合 + 回测

## 安装

```bash
cd "/Users/xinwei/Desktop/my show /concept_stock_agent"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 使用

```bash
# 基本用法：传入概念名，自动匹配 Tushare 概念板块
python run.py "AI算力"

# 指定 Tushare 概念代码（跳过模糊匹配）
python run.py "AI算力" --concept-code TS0001

# 跳过回测（只跑选股）
python run.py "AI算力" --skip-backtest

# 自定义回测区间
python run.py "AI算力" --backtest-start 20250101 --backtest-end 20260414
```

## 输出

每次运行会在 `outputs/` 下生成一份 JSON：
- 研究计划
- 产业链拆解
- 每个节点的股票推荐及理由
- 评审结论
- 最终组合

## 配置

`config.py` 中可调参数：
- `CHAIN_MIN/MAX_NODES`: 产业链环节数（默认 4-8）
- `STOCKS_PER_NODE_MIN/MAX`: 每环节股票数（默认 5-10）
- `PORTFOLIO_MAX_SIZE`: 最终组合容量（默认 30）
- `BENCHMARK`: 回测基准（默认沪深300）

## 升级到 Claude

改 `config.py`：
```python
DEEPSEEK_BASE_URL = "https://api.anthropic.com/v1"  # 或 Claude 兼容端点
DEEPSEEK_MODEL = "claude-sonnet-4-6"
```
并在 `.env` 替换 key。
