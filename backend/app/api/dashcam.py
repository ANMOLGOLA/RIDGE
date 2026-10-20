from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.core.db import get_db
from app.core.models import DashcamEvent, Incident, IncidentEvidence
from app.core.schemas import DashcamEventSchema
from app.dashcam.simulator import generate_simulated_dashcam_event
from app.dashcam.privacy import apply_privacy_blur
from app.pipeline.confidence import calculate_confidence

router = APIRouter(prefix="/dashcam", tags=["Dashcam DaaS"])

@router.get("/events", response_model=List[DashcamEventSchema])
def list_dashcam_events(db: Session = Depends(get_db)):
    return db.query(DashcamEvent).order_by(DashcamEvent.detected_at.desc()).limit(25).all()

@router.post("/simulate", response_model=DashcamEventSchema)
def trigger_simulated_event(
    vehicle_id: str = "veh_nh10_01",
    db: Session = Depends(get_db)
):
    """
    Simulates a hardware dashcam road hazard detection from a vehicle.
    Feeds directly into the shared Incident Layer with source=dashcam.
    """
    data = generate_simulated_dashcam_event(vehicle_id)

    # Create Dashcam event record
    event = DashcamEvent(
        vehicle_id=data["vehicle_id"],
        hazard_type=data["hazard_type"],
        corridor=data["corridor"],
        lat=data["lat"],
        lon=data["lon"],
        confidence=data["confidence"],
        image_url=data["image_url"],
        is_simulated=True,
        detected_at=data["detected_at"]
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Create or update shared Incident
    incident = Incident(
        title=f"Dashcam Alert: {data['hazard_type'].capitalize()} near {data['location_text']}",
        event_type="landslide" if data["hazard_type"] == "rockfall" else "waterlogging" if data["hazard_type"] == "waterlogging" else "road_closed",
        status="partially_open",
        road=data["corridor"],
        corridor=data["corridor"],
        location_text=data["location_text"],
        lat=data["lat"],
        lon=data["lon"],
        severity=4 if data["hazard_type"] == "rockfall" else 3,
        confidence=data["confidence"],
        confidence_breakdown={
            "source_reliability": 0.92,
            "corroboration_count": 1,
            "geocoding_precision": 0.99,
            "recency_decay": 1.0
        },
        provenance={
            "source_url": "ridge://dashcam/telemetry",
            "domain": "ridge-dashcam-network",
            "tinyfish_api": "Hardware Dashcam DaaS Stream",
            "fetched_at": data["detected_at"].isoformat(),
            "content_hash": f"dashcam_{event.id}"
        },
        source_count=1,
        summary=f"Automated edge detection of {data['hazard_type']} flagged by vehicle {vehicle_id} on {data['corridor']}.",
        evidence_quote=f"Visual edge inference detected {data['hazard_type']} with {int(data['confidence']*100)}% confidence.",
        lifecycle_state="active"
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    event.incident_id = incident.id
    db.commit()

    return event

@router.post("/upload")
async def upload_dashcam_frame(
    file: UploadFile = File(...),
    corridor: str = Form("NH-10"),
    hazard_type: str = Form("debris"),
    db: Session = Depends(get_db)
):
    """
    Accepts uploaded dashcam footage/image, applies OpenCV privacy blur,
    and returns detected hazard (flagged as prototype simulation).
    """
    contents = await file.read()
    blurred = apply_privacy_blur(contents)

    event = DashcamEvent(
        vehicle_id="upload_client_01",
        hazard_type=hazard_type,
        corridor=corridor,
        lat=27.0450 if corridor == "NH-10" else 26.0463,
        lon=88.4320 if corridor == "NH-10" else 91.8647,
        confidence=0.89,
        image_url="https://images.unsplash.com/photo-1541888946425-d0fbb18f156b?auto=format&fit=crop&w=600&q=80",
        is_simulated=True
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "event_id": event.id,
        "hazard_type": hazard_type,
        "privacy_blur_applied": True,
        "is_simulated": True,
        "confidence": event.confidence,
        "note": "Prototype simulation: OpenCV license plate blur applied; edge detection flagged as simulation."
    }
