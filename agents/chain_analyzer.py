"""Chain Analyzer: decompose concept into 4-8 industry chain segments."""
from data.deepseek_client import chat_json
from config import CHAIN_MIN_NODES, CHAIN_MAX_NODES

SYSTEM = f"""你是一名产业链研究专家。给定一个投资概念和研究计划，请将其拆解为 {CHAIN_MIN_NODES}-{CHAIN_MAX_NODES} 个一级产业链环节。

输出严格的 JSON 对象：
{{
  "chain_nodes": [
    {{
      "name": "环节名称（如：算力芯片）",
      "position": "上游/中游/下游",
      "description": "该环节在产业链中的角色（1-2句）",
      "market_logic": "该环节的市场逻辑与增长驱动（1-2句）"
    }},
    ...
  ]
}}

要求：
1. 环节数量在 {CHAIN_MIN_NODES}-{CHAIN_MAX_NODES} 之间
2. 覆盖上游、中游、下游全链条
3. 每个环节应是可投资的细分领域（有 A 股标的）
"""


def analyze(concept_name: str, plan_result: dict) -> dict:
    user = f"""概念：{concept_name}

研究计划：
- 概念定义：{plan_result.get('concept_summary')}
- 核心问题：{plan_result.get('key_questions')}
- 拆解方向：{plan_result.get('expected_chain_direction')}
- 投资逻辑：{plan_result.get('investment_thesis_hypothesis')}

请拆解产业链。"""
    return chat_json(SYSTEM, user)
