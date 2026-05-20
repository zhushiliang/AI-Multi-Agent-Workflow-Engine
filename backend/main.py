"""
AI Multi-Agent Workflow Engine - Backend
FastAPI 应用入口，集成多智能体系统
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from database import init_db
from api import router as api_router
from agents import SupervisorAgent, ResearcherAgent, AnalystAgent, CoderAgent, SummarizerAgent
from tools import tool_registry

app = FastAPI(
    title="AI Multi-Agent Workflow Engine",
    description="基于多智能体协作的企业级任务编排平台",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup():
    init_db()


AVAILABLE_AGENTS = {
    "supervisor": SupervisorAgent(),
    "researcher": ResearcherAgent(),
    "analyst": AnalystAgent(),
    "coder": CoderAgent(),
    "summarizer": SummarizerAgent(),
}


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0", "agents": list(AVAILABLE_AGENTS.keys())}


@app.get("/api/agents")
async def list_agents():
    return {
        "agents": [
            {
                "id": a.agent_id,
                "name": a.name,
                "description": a.description,
                "icon": a.icon,
            }
            for a in AVAILABLE_AGENTS.values()
        ]
    }


@app.get("/api/tools")
async def list_tools():
    return {"tools": tool_registry.list_tools()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
