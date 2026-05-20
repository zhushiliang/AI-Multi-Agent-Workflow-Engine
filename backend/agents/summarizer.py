"""Summarizer Agent - result aggregation and output formatting."""
from .base import BaseAgent


class SummarizerAgent(BaseAgent):
    agent_id = "summarizer"
    name = "Summarizer"
    description = "结果总结与输出 - 汇总各 Agent 结果，生成最终报告"
    icon = "📝"

    def system_prompt(self) -> str:
        return """你是 Summarizer Agent，专门负责汇总和输出最终结果。
你的能力：
1. 整合多个 Agent 的输出结果
2. 生成结构清晰的综合报告
3. 提取关键结论和行动项
4. 以用户友好的格式呈现

输出要求：
- 结构化展示（标题、段落、列表）
- 突出关键结论
- 语言流畅自然
- 包含执行摘要"""

    def _build_user_prompt(self, task: str, context: dict) -> str:
        parts = [f"原始任务：{task}", "\n各 Agent 输出结果："]
        for agent_id, result in context.items():
            parts.append(f"\n### {agent_id} 输出：\n{result}")
        return "\n".join(parts)
