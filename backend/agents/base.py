"""Base agent class with LLM integration and tool support."""
import json
from abc import ABC, abstractmethod
from typing import AsyncGenerator
from engine.llm import chat_completion, chat_completion_stream
from engine.message_bus import MessageBus, Message, bus


class BaseAgent(ABC):
    agent_id: str = "base"
    name: str = "Base Agent"
    description: str = ""
    icon: str = "🤖"

    def __init__(self, message_bus: MessageBus = bus):
        self.bus = message_bus
        self.bus.subscribe(self.agent_id, self._handle_message)

    @abstractmethod
    def system_prompt(self) -> str:
        ...

    @abstractmethod
    def _build_user_prompt(self, task: str, context: dict) -> str:
        ...

    async def _handle_message(self, message: Message):
        pass

    async def run(self, task: str, context: dict | None = None) -> str:
        context = context or {}
        user_prompt = self._build_user_prompt(task, context)
        messages = [{"role": "user", "content": user_prompt}]
        return await chat_completion(self.system_prompt(), messages)

    async def run_stream(self, task: str, context: dict | None = None) -> AsyncGenerator[str, None]:
        context = context or {}
        user_prompt = self._build_user_prompt(task, context)
        messages = [{"role": "user", "content": user_prompt}]
        async for chunk in chat_completion_stream(self.system_prompt(), messages):
            yield chunk

    async def delegate(self, target_agent_id: str, task: str, context: dict | None = None) -> str | None:
        response = await self.bus.request(Message(
            sender=self.agent_id,
            recipient=target_agent_id,
            content={"task": task, "context": context or {}},
            msg_type="delegate",
        ))
        return response.content if response else None
