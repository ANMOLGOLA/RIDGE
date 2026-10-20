from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.db import get_db
from app.core.schemas import RouteRequest, RouteResponse, RouteCompareResponse
from app.routing.planner import plan_routes, compare_routes

router = APIRouter(prefix="/routes", tags=["Routing"])

@router.post("", response_model=RouteResponse)
def calculate_routes(
    payload: RouteRequest,
    db: Session = Depends(get_db)
):
    """
    Computes up to 3 risk-aware alternative routes on the road graph:
    - Safest (AI Recommended): Avoids high-risk segments & active blockages
    - Balanced: Balances ETA with hazard prevention
    - Fastest / Direct: Unpenalized baseline
    """
    return plan_routes(
        db,
        origin_name=payload.origin,
        dest_name=payload.destination,
        preference=payload.preference,
        corridor=payload.corridor or "NH-10"
    )

@router.get("/compare", response_model=RouteCompareResponse)
def get_route_comparison(
    corridor: Optional[str] = Query("NH-10", description="Corridor code"),
    origin: Optional[str] = Query(None, description="Origin landmark"),
    destination: Optional[str] = Query(None, description="Destination landmark"),
    db: Session = Depends(get_db)
):
    """
    Returns comparative analytics between baseline direct route vs RIDGE safe route.
    Used for demo comparison charts and ROI evaluation.
    """
    return compare_routes(
        db,
        origin_name=origin,
        dest_name=destination,
        corridor=corridor or "NH-10"
    )
