"""Lightweight in-process message bus for inter-agent communication."""
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable


@dataclass
class Message:
    sender: str
    recipient: str
    content: Any
    msg_type: str = "task"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)


class MessageBus:
    def __init__(self):
        self._subscribers: dict[str, list[Callable[[Message], Awaitable[None]]]] = {}
        self._history: list[Message] = []
        self._lock = asyncio.Lock()

    def subscribe(self, agent_id: str, handler: Callable[[Message], Awaitable[None]]):
        self._subscribers.setdefault(agent_id, []).append(handler)

    async def publish(self, message: Message):
        async with self._lock:
            self._history.append(message)
        handlers = self._subscribers.get(message.recipient, [])
        for handler in handlers:
            asyncio.create_task(handler(message))

    async def request(self, message: Message, timeout: float = 120.0) -> Message | None:
        future: asyncio.Future[Message] = asyncio.get_event_loop().create_future()

        async def response_handler(msg: Message):
            if not future.done():
                future.set_result(msg)

        self.subscribe(message.recipient, response_handler)
        await self.publish(message)
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def get_history(self, limit: int = 100) -> list[Message]:
        return self._history[-limit:]


bus = MessageBus()
