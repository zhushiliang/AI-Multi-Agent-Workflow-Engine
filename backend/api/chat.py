"""Chat API with SSE streaming and multi-agent workflow execution."""
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Conversation, Message
from agents import SupervisorAgent, ResearcherAgent, AnalystAgent, CoderAgent, SummarizerAgent
from engine.workflow import WorkflowEngine

router = APIRouter()

agents = {
    "supervisor": SupervisorAgent(),
    "researcher": ResearcherAgent(),
    "analyst": AnalystAgent(),
    "coder": CoderAgent(),
    "summarizer": SummarizerAgent(),
}
engine = WorkflowEngine(agents)


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None
    stream: bool = True


@router.post("/send")
async def chat_send(request: ChatRequest, db: Session = Depends(get_db)):
    if request.conversation_id is None:
        conv = Conversation(title=request.message[:50])
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversation_id = conv.id
    else:
        conversation_id = request.conversation_id

    db.add(Message(conversation_id=conversation_id, role="user", content=request.message))
    db.commit()

    if not request.stream:
        supervisor = agents["supervisor"]
        plan = await supervisor.route(request.message)
        full_result = ""
        async for event in engine.execute_plan(plan, request.message):
            if event["type"] == "results":
                results = event["data"]
                if "summarizer" in results:
                    full_result = results["summarizer"]
                elif results:
                    full_result = list(results.values())[-1]

        db.add(Message(conversation_id=conversation_id, role="assistant", content=full_result))
        db.commit()
        return {
            "conversation_id": conversation_id,
            "response": full_result,
        }

    return StreamingResponse(
        _stream_response(request.message, conversation_id, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def _stream_response(message: str, conversation_id: int, db: Session):
    supervisor = agents["supervisor"]

    try:
        plan = await supervisor.route(message)
        yield f"data: {json.dumps({'type': 'plan', 'data': plan}, ensure_ascii=False)}\n\n"

        full_result = ""
        async for event in engine.execute_plan_stream(plan, message):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            if event["type"] == "results":
                results = event["data"]
                if "summarizer" in results:
                    full_result = results["summarizer"]
                elif results:
                    full_result = list(results.values())[-1]

        if full_result:
            db.add(Message(conversation_id=conversation_id, role="assistant", content=full_result))
            db.commit()

        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'data': {'message': str(e)}}, ensure_ascii=False)}\n\n"


@router.get("/conversations")
async def list_conversations(db: Session = Depends(get_db)):
    convs = db.query(Conversation).order_by(Conversation.updated_at.desc()).limit(50).all()
    return {"conversations": [{"id": c.id, "title": c.title, "created_at": c.created_at.isoformat()} for c in convs]}


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    msgs = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    return {"messages": [{"id": m.id, "role": m.role, "agent_id": m.agent_id, "content": m.content, "created_at": m.created_at.isoformat()} for m in msgs]}
