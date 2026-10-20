from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.core.db import get_db
from app.core.models import RoadSegment, RiskScore
from app.core.schemas import GeoJSONFeatureCollection, GeoJSONFeature

router = APIRouter(prefix="/risk", tags=["Risk"])

@router.get("/segments", response_model=GeoJSONFeatureCollection)
def get_risk_segments(
    corridor: Optional[str] = Query(None, description="Filter by corridor e.g. NH-10 or NH-6"),
    db: Session = Depends(get_db)
):
    """
    Returns road segments with their real-time or modeled risk scores as a GeoJSON FeatureCollection.
    Risk levels:
    - < 0.35: 'open' (Green)
    - 0.35 - 0.65: 'risky' (Amber)
    - > 0.65: 'high_risk' (Red)
    - 1.0 (or confirmed blocked): 'blocked' (Black)
    """
    query = db.query(RoadSegment)
    if corridor:
        query = query.filter(RoadSegment.corridor == corridor)
    
    segments = query.all()
    features = []

    for seg in segments:
        risk = seg.risk_score
        score = risk.risk_score if risk else 0.1
        label = risk.risk_label if risk else "open"
        explanation = risk.explanation if risk else "Standard baseline conditions"

        feat = GeoJSONFeature(
            type="Feature",
            geometry={
                "type": "LineString",
                "coordinates": seg.coordinates_json
            },
            properties={
                "id": seg.id,
                "edge_id": seg.edge_id,
                "corridor": seg.corridor,
                "road_name": seg.road_name,
                "name": seg.name,
                "start_node": seg.start_node,
                "end_node": seg.end_node,
                "start_lat": seg.start_lat,
                "start_lon": seg.start_lon,
                "end_lat": seg.end_lat,
                "end_lon": seg.end_lon,
                "length_m": seg.length_m,
                "base_travel_time_sec": seg.base_travel_time_sec,
                "slope_deg": seg.slope_deg,
                "river_proximity_m": seg.river_proximity_m,
                "landslide_zone": seg.landslide_zone,
                "historical_incident_count": seg.historical_incident_count,
                "risk_score": score,
                "risk_label": label,
                "explanation": explanation
            }
        )
        features.append(feat)

    return GeoJSONFeatureCollection(features=features)
