from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.core.db import get_db
from app.core.models import Vehicle, VehiclePosition
from app.core.schemas import VehicleSchema

router = APIRouter(prefix="/fleet", tags=["Fleet"])

@router.get("/vehicles", response_model=List[VehicleSchema])
def list_vehicles(
    corridor: Optional[str] = Query(None, description="Corridor filter"),
    db: Session = Depends(get_db)
):
    query = db.query(Vehicle)
    if corridor:
        query = query.filter(Vehicle.corridor == corridor)
    return query.all()

@router.post("/vehicles/{vehicle_id}/position")
def update_vehicle_position(
    vehicle_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    veh = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not veh:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    lat = float(payload.get("lat", veh.current_lat))
    lon = float(payload.get("lon", veh.current_lon))
    speed = float(payload.get("speed_kmh", 40.0))

    veh.current_lat = lat
    veh.current_lon = lon
    veh.updated_at = datetime.now(timezone.utc)

    pos = VehiclePosition(
        vehicle_id=veh.id,
        lat=lat,
        lon=lon,
        speed_kmh=speed
    )
    db.add(pos)
    db.commit()
    return {"status": "updated", "vehicle_id": veh.id, "lat": lat, "lon": lon}
