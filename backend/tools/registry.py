"""Tool registry with dynamic loading and execution."""
import inspect
import json
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    function: Callable
    parameters: dict = field(default_factory=dict)

    def to_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, parameters: dict | None = None):
        def decorator(func):
            self._tools[name] = Tool(
                name=name,
                description=description,
                function=func,
                parameters=parameters or {},
            )
            return func
        return decorator

    def add_tool(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict]:
        return [t.to_schema() for t in self._tools.values()]

    async def execute(self, name: str, **kwargs) -> Any:
        tool = self._tools.get(name)
        if not tool:
            return f"Tool '{name}' not found"
        if inspect.iscoroutinefunction(tool.function):
            return await tool.function(**kwargs)
        return tool.function(**kwargs)


tool_registry = ToolRegistry()


@tool_registry.register("web_search", "搜索互联网获取信息", {"query": {"type": "string", "description": "搜索关键词"}})
async def web_search(query: str) -> str:
    return f"[搜索结果] 关于 '{query}'：这是一个模拟的搜索结果。在生产环境中，这里会调用真实的搜索 API。"


@tool_registry.register("code_execute", "执行 Python 代码", {"code": {"type": "string", "description": "Python 代码"}})
async def code_execute(code: str) -> str:
    try:
        result = {}
        exec(code, {"__builtins__": {}}, result)
        return f"[执行结果] {result}"
    except Exception as e:
        return f"[执行错误] {type(e).__name__}: {e}"


@tool_registry.register("calculator", "数学计算", {"expression": {"type": "string", "description": "数学表达式"}})
async def calculator(expression: str) -> str:
    try:
        allowed = set("0123456789+-*/.() ")
        if all(c in allowed for c in expression):
            result = eval(expression)
            return f"[计算结果] {expression} = {result}"
        return "[错误] 不支持的表达式"
    except Exception as e:
        return f"[计算错误] {e}"


@tool_registry.register("json_parse", "解析 JSON 数据", {"text": {"type": "string", "description": "JSON 字符串"}})
async def json_parse(text: str) -> str:
    try:
        data = json.loads(text)
        return f"[解析结果] {json.dumps(data, ensure_ascii=False, indent=2)}"
    except json.JSONDecodeError as e:
        return f"[JSON 解析错误] {e}"
