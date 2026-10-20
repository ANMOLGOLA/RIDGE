from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timezone
from app.core.db import get_db
from app.core.models import Incident, IncidentEvidence, Verification, RoadSegment, RiskScore
from app.core.schemas import IncidentSchema, VerificationRequest

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentSchema])
def list_incidents(
    corridor: Optional[str] = Query(None, description="Filter by corridor e.g. NH-10 or NH-6"),
    status: Optional[str] = Query(None, description="Filter by status e.g. blocked, partially_open, open"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence threshold"),
    max_confidence: Optional[float] = Query(None, description="Maximum confidence threshold (for verification queue)"),
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if corridor:
        query = query.filter(Incident.corridor == corridor)
    if status:
        query = query.filter(Incident.status == status)
    if min_confidence is not None:
        query = query.filter(Incident.confidence >= min_confidence)
    if max_confidence is not None:
        query = query.filter(Incident.confidence <= max_confidence)
    
    return query.order_by(Incident.created_at.desc()).all()

@router.get("/{incident_id}", response_model=IncidentSchema)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc

@router.post("/{incident_id}/verify", response_model=IncidentSchema)
def verify_incident(
    incident_id: str,
    payload: VerificationRequest,
    db: Session = Depends(get_db)
):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    now = datetime.now(timezone.utc)
    verification = Verification(
        incident_id=inc.id,
        verifier=payload.verifier or "Authority Officer",
        decision=payload.decision,
        note=payload.note,
        verified_at=now
    )
    db.add(verification)

    inc.verified_by = payload.verifier or "Authority Officer"
    inc.verification_note = payload.note
    inc.updated_at = now

    if payload.decision == "confirm":
        inc.confidence = min(1.0, inc.confidence + 0.35)
        if inc.status == "unknown":
            inc.status = "blocked"
        # Update segment risk score
        if inc.nearest_segment_id:
            risk = db.query(RiskScore).filter(RiskScore.segment_id == inc.nearest_segment_id).first()
            if risk:
                risk.risk_score = 1.0 if inc.status == "blocked" else 0.75
                risk.risk_label = "blocked" if inc.status == "blocked" else "high_risk"
                risk.explanation = f"Verified by {inc.verified_by}: {inc.title}"
    else:  # reject
        inc.confidence = max(0.05, inc.confidence - 0.45)
        inc.lifecycle_state = "resolved"
        inc.status = "open"
        if inc.nearest_segment_id:
            risk = db.query(RiskScore).filter(RiskScore.segment_id == inc.nearest_segment_id).first()
            if risk and "Verified" in (risk.explanation or ""):
                risk.risk_score = 0.20
                risk.risk_label = "open"
                risk.explanation = "Report rejected by authority verification."

    db.commit()
    db.refresh(inc)
    return inc
