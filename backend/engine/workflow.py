"""Workflow execution engine - orchestrates multi-agent collaboration."""
import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import AsyncGenerator, Any
from .message_bus import Message, MessageBus, bus


@dataclass
class WorkflowStep:
    agent_id: str
    task: str
    priority: int = 1
    depends_on: list[str] = field(default_factory=list)


@dataclass
class StepResult:
    agent_id: str
    task: str
    result: str
    status: str = "success"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class WorkflowEngine:
    def __init__(self, agents: dict[str, Any], message_bus: MessageBus = bus):
        self.agents = agents
        self.bus = message_bus

    async def execute_plan(self, plan: dict, original_task: str) -> AsyncGenerator[dict, None]:
        steps = plan.get("steps", [])
        plan_desc = plan.get("plan", "")
        results: dict[str, str] = {}

        yield {"type": "plan", "data": {"plan": plan_desc, "step_count": len(steps)}}

        sorted_steps = sorted(steps, key=lambda s: s.get("priority", 1))

        for step in sorted_steps:
            agent_id = step["agent"]
            task = step["task"]
            agent = self.agents.get(agent_id)

            if not agent:
                yield {"type": "error", "data": {"agent": agent_id, "message": f"Agent '{agent_id}' not found"}}
                continue

            yield {
                "type": "step_start",
                "data": {"agent_id": agent_id, "agent_name": agent.name, "task": task},
            }

            context = {"background": original_task}
            context.update(results)

            try:
                result = await agent.run(task, context)
                results[agent_id] = result
                yield {
                    "type": "step_complete",
                    "data": {"agent_id": agent_id, "result": result},
                }
            except Exception as e:
                yield {
                    "type": "step_error",
                    "data": {"agent_id": agent_id, "error": str(e)},
                }

        yield {"type": "results", "data": results}

    async def execute_plan_stream(self, plan: dict, original_task: str) -> AsyncGenerator[dict, None]:
        steps = plan.get("steps", [])
        plan_desc = plan.get("plan", "")
        results: dict[str, str] = {}

        yield {"type": "plan", "data": {"plan": plan_desc, "step_count": len(steps)}}

        sorted_steps = sorted(steps, key=lambda s: s.get("priority", 1))

        for step in sorted_steps:
            agent_id = step["agent"]
            task = step["task"]
            agent = self.agents.get(agent_id)

            if not agent:
                yield {"type": "error", "data": {"agent": agent_id, "message": f"Agent '{agent_id}' not found"}}
                continue

            yield {
                "type": "step_start",
                "data": {"agent_id": agent_id, "agent_name": agent.name, "task": task},
            }

            context = {"background": original_task}
            context.update(results)

            try:
                full_result = ""
                async for chunk in agent.run_stream(task, context):
                    full_result += chunk
                    yield {"type": "step_chunk", "data": {"agent_id": agent_id, "chunk": chunk}}

                results[agent_id] = full_result
                yield {
                    "type": "step_complete",
                    "data": {"agent_id": agent_id, "result": full_result},
                }
            except Exception as e:
                yield {
                    "type": "step_error",
                    "data": {"agent_id": agent_id, "error": str(e)},
                }

        yield {"type": "results", "data": results}
