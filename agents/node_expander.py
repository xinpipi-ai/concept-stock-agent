"""Node Expander: pick 5-10 stocks per chain node, classify core/satellite.

Uses Tushare's concept stock list as the candidate pool (replaces Gangtise RAG).
"""
from data.deepseek_client import chat_json
from data import tushare_client
from config import STOCKS_PER_NODE_MIN, STOCKS_PER_NODE_MAX

SYSTEM = f"""你是一名 A 股个股分析师。给定某一产业链环节和候选股票池，请从候选池中挑选 {STOCKS_PER_NODE_MIN}-{STOCKS_PER_NODE_MAX} 只代表性 A 股。

输出严格的 JSON 对象：
{{
  "picks": [
    {{
      "ts_code": "股票代码（如 000001.SZ）",
      "name": "股票简称",
      "bucket": "core 或 satellite",
      "rationale": "为何入选该环节（1-2句，要具体，不要套话）"
    }},
    ...
  ]
}}

规则：
- core（核心持仓）：该环节的龙头或确定性最高的标的
- satellite（卫星持仓）：弹性标的或细分领域优势公司
- 只从候选池中挑，不要编造不在池里的股票
- 若候选池不足，宁可少选，不要凑数
- 若候选池里根本没有匹配这个环节的股票，返回 picks: []
"""


def expand(concept_name: str, node: dict, candidate_pool: list[dict]) -> dict:
    """Pick stocks for a single chain node from the candidate pool.

    candidate_pool: list of dicts with ts_code, name, industry
    """
    pool_str = "\n".join(
        f"- {s['ts_code']} {s['name']}（行业：{s.get('industry', '-')}）"
        for s in candidate_pool
    )
    user = f"""概念：{concept_name}

产业链环节：
- 名称：{node['name']}（{node.get('position')}）
- 角色：{node.get('description')}
- 市场逻辑：{node.get('market_logic')}

候选股票池（来自概念成分股，按 Tushare 概念板块）：
{pool_str}

请挑选。"""
    return chat_json(SYSTEM, user)


def build_candidate_pool(concept_code: str) -> list[dict]:
    """Build candidate pool from Tushare concept stocks + industry metadata."""
    concept_df = tushare_client.concept_stocks(concept_code)
    ts_codes = concept_df["ts_code"].tolist()
    if not ts_codes:
        return []
    enriched = tushare_client.enrich_stocks_with_industry(ts_codes)
    return enriched.to_dict(orient="records")
