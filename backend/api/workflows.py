"""Workflow CRUD API."""
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import WorkflowRecord

router = APIRouter()


class WorkflowCreate(BaseModel):
    name: str
    description: str = ""
    definition: dict


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    definition: dict | None = None


@router.post("")
async def create_workflow(request: WorkflowCreate, db: Session = Depends(get_db)):
    wf = WorkflowRecord(
        name=request.name,
        description=request.description,
        definition_json=json.dumps(request.definition),
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return {
        "id": wf.id,
        "name": wf.name,
        "description": wf.description,
        "definition": request.definition,
    }


@router.get("")
async def list_workflows(db: Session = Depends(get_db)):
    wfs = db.query(WorkflowRecord).order_by(WorkflowRecord.updated_at.desc()).all()
    return {
        "workflows": [
            {
                "id": w.id,
                "name": w.name,
                "description": w.description,
                "definition": json.loads(w.definition_json),
            }
            for w in wfs
        ]
    }


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    wf = db.query(WorkflowRecord).filter(WorkflowRecord.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {
        "id": wf.id,
        "name": wf.name,
        "description": wf.description,
        "definition": json.loads(wf.definition_json),
    }


@router.put("/{workflow_id}")
async def update_workflow(workflow_id: int, request: WorkflowUpdate, db: Session = Depends(get_db)):
    wf = db.query(WorkflowRecord).filter(WorkflowRecord.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if request.name is not None:
        wf.name = request.name
    if request.description is not None:
        wf.description = request.description
    if request.definition is not None:
        wf.definition_json = json.dumps(request.definition)
    db.commit()
    return {"status": "updated"}


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    wf = db.query(WorkflowRecord).filter(WorkflowRecord.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(wf)
    db.commit()
    return {"status": "deleted"}
