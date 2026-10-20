from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.core.models import Incident
from app.pipeline.geocode import haversine_dist

def find_duplicate_incident(
    db: Session,
    corridor: str,
    event_type: str,
    lat: Optional[float],
    lon: Optional[float],
    max_distance_km: float = 2.0,
    max_hours: float = 6.0
) -> Optional[Incident]:
    """
    Step 6: Deduplication Check.
    Matches existing active incidents with same corridor + event_type + within 2km + within 6 hours.
    """
    if lat is None or lon is None:
        return None

    time_threshold = datetime.now(timezone.utc) - timedelta(hours=max_hours)
    candidates = db.query(Incident).filter(
        Incident.corridor == corridor,
        Incident.event_type == event_type,
        Incident.lifecycle_state == "active",
        Incident.created_at >= time_threshold
    ).all()

    for cand in candidates:
        if cand.lat is not None and cand.lon is not None:
            dist_m = haversine_dist(lat, lon, cand.lat, cand.lon)
            if dist_m <= (max_distance_km * 1000.0):
                return cand

    return None
