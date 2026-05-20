"""Analyst Agent - data analysis and logical reasoning."""
from .base import BaseAgent


class AnalystAgent(BaseAgent):
    agent_id = "analyst"
    name = "Analyst"
    description = "数据推理与分析 - 逻辑推理、数据处理、趋势预测"
    icon = "📊"

    def system_prompt(self) -> str:
        return """你是 Analyst Agent，专门负责数据分析与逻辑推理。
你的能力：
1. 深度分析问题，找出核心矛盾和关键因素
2. 进行逻辑推理和因果分析
3. 数据处理和统计分析
4. 趋势预测和风险评估
5. 生成可视化友好的分析报告

输出要求：
- 逻辑严密，论据充分
- 包含数据支撑
- 给出明确的结论和建议"""

    def _build_user_prompt(self, task: str, context: dict) -> str:
        parts = [f"分析任务：{task}"]
        if context:
            parts.append(f"数据/背景：{context.get('data', '无')}")
            parts.append(f"研究资料：{context.get('research', '无')}")
        return "\n".join(parts)
