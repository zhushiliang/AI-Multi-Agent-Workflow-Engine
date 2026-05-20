"""Researcher Agent - information retrieval and knowledge synthesis."""
from .base import BaseAgent


class ResearcherAgent(BaseAgent):
    agent_id = "researcher"
    name = "Researcher"
    description = "信息检索与收集 - 搜索资料、整合知识、生成调研报告"
    icon = "🔍"

    def system_prompt(self) -> str:
        return """你是 Researcher Agent，专门负责信息检索与知识整合。
你的能力：
1. 根据主题搜索和整理相关信息
2. 从多个角度分析问题背景
3. 生成结构化的调研报告
4. 提供可靠的信息来源和依据

输出要求：
- 结构清晰，使用标题和分段
- 包含关键数据和事实
- 标注信息来源（如有）"""

    def _build_user_prompt(self, task: str, context: dict) -> str:
        parts = [f"调研任务：{task}"]
        if context:
            parts.append(f"背景信息：{context.get('background', '无')}")
        return "\n".join(parts)
