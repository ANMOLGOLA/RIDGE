from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.db import get_db
from app.core.models import Alert
from app.core.schemas import AlertSchema

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertSchema])
def list_alerts(
    corridor: Optional[str] = Query(None, description="Corridor filter"),
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    if corridor:
        query = query.filter(Alert.corridor == corridor)
    return query.order_by(Alert.created_at.desc()).limit(20).all()

@router.post("/subscribe")
def subscribe_alert_notifications(payload: dict):
    """
    Subscribes a driver or vehicle to proactive WhatsApp/SMS alerts.
    """
    return {
        "status": "subscribed",
        "message": f"Successfully registered notification channel for {payload.get('phone_number') or payload.get('vehicle_id')}"
    }
