# 🌌 AI Multi-Agent Workflow Engine

> 基于多智能体协作的企业级任务编排平台，支持链式推理、SSE 流式输出与可视化工作流。

**项目名称：AI-Multi-Agent-Workflow-Engine**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)
![React](https://img.shields.io/badge/React-18-61dafb.svg)
![Claude](https://img.shields.io/badge/Claude-Anthropic-orange.svg)

---

## 📖 项目简介

本项目是一个**真正可运行的多智能体协作系统**，通过 Agent 之间的分工与协调，完成复杂的多步骤任务。

### 🎯 解决的核心痛点

1. **单一 Agent 能力瓶颈**：单个 LLM 难以同时处理信息检索、数据分析、代码生成等跨领域任务。
2. **缺乏任务编排**：非技术人员无法灵活定义 AI 工作流。
3. **缺少实时反馈**：用户无法看到 Agent 协作的实时过程。

### 🔗 核心逻辑流

```
用户输入
    ↓
Supervisor Agent (意图识别 + 任务分解 + 路由分发)
    ↓
┌─────────────┬─────────────┬─────────────┐
│ Researcher  │   Analyst   │    Coder    │
│ 信息检索    │  数据分析    │  代码生成    │
└─────────────┴─────────────┴─────────────┘
    ↓
Summarizer Agent (结果汇总 + 结构化输出)
    ↓
用户收到最终结果
```

- **长链推理**：Supervisor 自动将复杂任务分解为多个子任务，分配给专业 Agent 串行/并行执行。
- **多 Agent 协作**：通过进程内消息总线实现代理间通信，上游 Agent 的输出自动传递给下游。
- **SSE 流式输出**：每个 Agent 的推理过程实时推送到前端，用户可看到完整的协作过程。

---

## ✨ 主要功能

| 功能模块 | 说明 | 状态 |
|---------|------|------|
| 🧠 智能路由 | Supervisor 分析意图，自动分配 Agent | ✅ 已实现 |
| 🔍 信息检索 | Researcher Agent 生成调研报告 | ✅ 已实现 |
| 📊 数据分析 | Analyst Agent 进行逻辑推理 | ✅ 已实现 |
| 💻 代码生成 | Coder Agent 编写和审查代码 | ✅ 已实现 |
| 📝 结果汇总 | Summarizer Agent 输出最终报告 | ✅ 已实现 |
| 🔧 工具注册 | 可扩展的工具注册中心（搜索/代码执行/计算） | ✅ 已实现 |
| 📊 可视化画布 | ReactFlow 拖拽式工作流可视化 | ✅ 已实现 |
| 💬 对话界面 | 实时 SSE 流式对话，展示 Agent 协作过程 | ✅ 已实现 |
| 💾 会话持久化 | SQLite 存储对话历史 | ✅ 已实现 |
| 🚀 SSE 流式输出 | Server-Sent Events 实时推送 | ✅ 已实现 |

---

## 🛠️ 技术栈

- **后端**: Python 3.10+ / FastAPI / SQLAlchemy / Anthropic SDK
- **前端**: React 18 / TypeScript / Tailwind CSS / ReactFlow
- **AI 引擎**: Anthropic Claude (支持自定义模型)
- **数据库**: SQLite (开箱即用)
- **通信**: SSE (Server-Sent Events) + 进程内消息总线

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- Anthropic API Key

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/AI-Multi-Agent-Workflow-Engine.git
cd AI-Multi-Agent-Workflow-Engine

# 2. 配置环境变量
cd backend
cp .env.example .env
# 编辑 .env 填入 ANTHROPIC_API_KEY

# 3. 安装后端依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. 启动后端
uvicorn main:app --reload --port 8000

# 5. 安装前端依赖（新终端）
cd ../frontend
npm install

# 6. 启动前端
npm run dev
```

访问 http://localhost:3000 即可体验。

---

## 📁 项目结构

```
AI-Multi-Agent-Workflow-Engine/
├── backend/
│   ├── agents/                 # Agent 定义
│   │   ├── __init__.py
│   │   ├── base.py             # Agent 基类（LLM 调用、流式输出、消息委托）
│   │   ├── supervisor.py       # 任务路由 Agent
│   │   ├── researcher.py       # 信息检索 Agent
│   │   ├── analyst.py          # 数据分析 Agent
│   │   ├── coder.py            # 代码生成 Agent
│   │   └── summarizer.py       # 结果汇总 Agent
│   ├── engine/                 # 核心引擎
│   │   ├── __init__.py
│   │   ├── llm.py              # Anthropic Claude API 客户端
│   │   ├── message_bus.py      # 进程内消息总线
│   │   └── workflow.py         # 工作流执行引擎
│   ├── tools/                  # 工具注册中心
│   │   ├── __init__.py
│   │   └── registry.py         # 工具注册与执行
│   ├── api/                    # API 路由
│   │   ├── __init__.py
│   │   ├── chat.py             # 对话 API（含 SSE 流式）
│   │   └── workflows.py        # 工作流 CRUD
│   ├── main.py                 # FastAPI 入口
│   ├── config.py               # 配置加载
│   ├── database.py             # SQLAlchemy 初始化
│   ├── models.py               # 数据库模型
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # 主界面（工作流画布 + 对话面板）
│   │   ├── main.tsx            # React 入口
│   │   └── styles/
│   │       └── index.css       # 暗色主题样式
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
├── .github/workflows/ci.yml   # CI 流水线
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔧 API 文档

启动后端后访问 http://localhost:8000/docs 查看 Swagger 文档。

### 核心接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat/send` | 发送消息（支持 SSE 流式） |
| GET | `/api/chat/conversations` | 获取对话列表 |
| GET | `/api/chat/conversations/{id}/messages` | 获取对话消息 |
| GET | `/api/agents` | 获取 Agent 列表 |
| GET | `/api/tools` | 获取工具列表 |
| POST | `/api/workflows` | 创建工作流 |
| GET | `/api/workflows` | 获取工作流列表 |

---

## 🤝 参与贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

---

## 📄 开源协议

本项目采用 MIT License 开源协议。

---

## 🙏 致谢

- [Anthropic](https://www.anthropic.com/) - Claude API
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Web 框架
- [ReactFlow](https://reactflow.dev/) - 可视化节点编辑器
- [LangChain](https://langchain.com/) - AI 应用开发框架
