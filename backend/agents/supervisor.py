"""Supervisor Agent - routes tasks to appropriate worker agents."""
import json
from .base import BaseAgent
from engine.message_bus import Message


class SupervisorAgent(BaseAgent):
    agent_id = "supervisor"
    name = "Supervisor"
    description = "任务路由与调度 - 分析用户意图，将子任务分配给专业 Agent"
    icon = "🧠"

    ROUTE_PROMPT = """你是一个任务调度专家。根据用户输入，决定需要哪些 Agent 协作完成任务。

可用的 Agent：
- researcher: 信息检索、知识查询、资料收集
- analyst: 数据分析、逻辑推理、趋势判断
- coder: 代码生成、代码审查、技术方案

请返回 JSON 格式的路由计划：
{
  "plan": "简要说明任务分解方案",
  "steps": [
    {"agent": "agent_id", "task": "具体子任务", "priority": 1}
  ]
}

只返回 JSON，不要其他内容。"""

    def system_prompt(self) -> str:
        return """你是 Supervisor Agent，负责任务调度。
收到用户任务后，你需要：
1. 分析任务需要哪些专业能力
2. 将任务分解为子任务
3. 返回 JSON 路由计划"""

    def _build_user_prompt(self, task: str, context: dict) -> str:
        return f"用户任务：{task}\n\n请分析并返回路由计划（JSON）。"

    async def route(self, task: str) -> dict:
        result = await self.run(task)
        try:
            json_str = result.strip()
            if json_str.startswith("```"):
                json_str = json_str.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(json_str)
        except (json.JSONDecodeError, IndexError):
            return {
                "plan": f"直接处理任务：{task}",
                "steps": [{"agent": "analyst", "task": task, "priority": 1}],
            }
