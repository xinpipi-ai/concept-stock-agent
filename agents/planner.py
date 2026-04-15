"""Planner: generate a research plan for a given concept."""
from data.deepseek_client import chat_json

SYSTEM = """你是一名资深卖方金工分析师，擅长产业链拆解与A股主题投资。你的任务是为给定的投资概念生成一份结构化研究计划。

输出必须是严格的 JSON 对象，字段：
- concept_summary: 对该概念的一句话定义（不超过50字）
- key_questions: 3-5 个待回答的核心研究问题（数组）
- expected_chain_direction: 产业链拆解的主方向（如"从算力硬件到应用落地"）
- investment_thesis_hypothesis: 该概念的投资逻辑假设（1-2句）
"""


def plan(concept_name: str) -> dict:
    user = f"请为以下投资概念生成研究计划：{concept_name}"
    return chat_json(SYSTEM, user)
