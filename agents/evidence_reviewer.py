"""Evidence Reviewer: check consistency, flag conflicts, remove duplicates."""
from collections import Counter
from data.deepseek_client import chat_json

SYSTEM = """你是一名投研组合审查员。给定产业链拆解结果和各环节推荐的股票，请审查整体逻辑一致性并给出评审意见。

输出严格的 JSON 对象：
{
  "logic_score": 0-10 的整数，表示整体逻辑完整性,
  "conflicts": ["冲突或重复问题的文字描述", ...],
  "missing_links": ["遗漏的关键环节（如有）", ...],
  "recommendation": "整体建议（如：可以进入组合构建 / 需要补充XX环节 / 某些股票归类不当）"
}
"""


def review(concept_name: str, chain_result: dict, node_picks: dict) -> dict:
    """
    node_picks: {node_name: {"picks": [...]}}
    """
    picks_str = ""
    all_codes = []
    for node_name, result in node_picks.items():
        picks_str += f"\n【{node_name}】\n"
        for p in result.get("picks", []):
            picks_str += f"  - {p['ts_code']} {p['name']} [{p['bucket']}] {p['rationale']}\n"
            all_codes.append(p["ts_code"])

    # Statistical checks
    dup_codes = [c for c, n in Counter(all_codes).items() if n > 1]
    stats_note = ""
    if dup_codes:
        stats_note = f"\n注意：以下股票在多个环节重复出现：{dup_codes}"

    chain_str = "\n".join(
        f"- {n['name']}（{n.get('position')}）"
        for n in chain_result.get("chain_nodes", [])
    )

    user = f"""概念：{concept_name}

产业链环节：
{chain_str}

各环节推荐股票：
{picks_str}
{stats_note}

请审查。"""
    result = chat_json(SYSTEM, user)
    result["_duplicates"] = dup_codes  # Pass stats to portfolio_builder
    return result
