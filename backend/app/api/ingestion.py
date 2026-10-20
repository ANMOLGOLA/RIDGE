import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.db import get_db, SessionLocal
from app.core.models import IngestionRun, IngestionStep
from app.core.schemas import IngestionRunRequest, IngestionRunSchema
from app.pipeline.runner import run_ingestion_pipeline

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])

def run_pipeline_task(run_corridor: str, mode: str, target_url: Optional[str]):
    db = SessionLocal()
    try:
        # Run async event loop for background pipeline task
        asyncio.run(run_ingestion_pipeline(db, corridor=run_corridor, mode=mode, target_url=target_url))
    finally:
        db.close()

@router.post("/run")
async def trigger_ingestion(
    payload: IngestionRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger a live or URL-based TinyFish ingestion run.
    mode="search": Searches for fresh corridor advisories via TinyFish Search.
    mode="url": Pastes a single advisory URL directly into TinyFish Fetch.
    """
    # Run synchronously or in background; for immediate demo feedback, we can run it asynchronously
    # and return run_id immediately, or run it directly so response has immediate result.
    run = await run_ingestion_pipeline(db, corridor=payload.corridor, mode=payload.mode, target_url=payload.url)
    return {
        "run_id": run.id,
        "status": run.status,
        "new_incidents_count": run.new_incidents_count,
        "duration_ms": run.duration_ms,
        "message": f"Successfully processed {payload.corridor} via TinyFish {run.tinyfish_api_used}"
    }

@router.get("/runs", response_model=List[IngestionRunSchema])
def list_ingestion_runs(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    return db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(limit).all()

@router.get("/runs/{run_id}", response_model=IngestionRunSchema)
def get_ingestion_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(IngestionRun).filter(IngestionRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return run
