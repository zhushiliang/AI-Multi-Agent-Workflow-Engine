"""Coder Agent - code generation and technical implementation."""
from .base import BaseAgent


class CoderAgent(BaseAgent):
    agent_id = "coder"
    name = "Coder"
    description = "代码生成与执行 - 编程实现、代码审查、技术方案"
    icon = "💻"

    def system_prompt(self) -> str:
        return """你是 Coder Agent，专门负责代码生成与技术实现。
你的能力：
1. 根据需求生成高质量代码
2. 支持 Python, JavaScript/TypeScript, Go, Rust 等语言
3. 代码审查和优化建议
4. 技术方案设计和架构建议
5. 调试和错误修复

输出要求：
- 代码语法正确，可直接运行
- 包含必要的注释
- 遵循语言最佳实践
- 提供使用说明"""

    def _build_user_prompt(self, task: str, context: dict) -> str:
        parts = [f"编程任务：{task}"]
        if context:
            parts.append(f"分析结论：{context.get('analysis', '无')}")
            parts.append(f"技术要求：{context.get('requirements', '无')}")
        return "\n".join(parts)
