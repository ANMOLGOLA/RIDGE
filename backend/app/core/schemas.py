from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

class ExtractedEvent(BaseModel):
    event_type: Literal[
        "landslide", "flood", "waterlogging", "road_closed", 
        "bridge_damage", "accident", "restored", "other"
    ]
    status: Literal["blocked", "partially_open", "open", "unknown"]
    road: Optional[str] = None
    location_text: str
    severity: int = Field(ge=1, le=5)
    occurred_at: Optional[datetime] = None
    summary: str
    evidence_quote: str

class IncidentEvidenceItem(BaseModel):
    id: str
    source_url: str
    domain: str
    snippet: str
    tinyfish_endpoint: str
    extracted_at: datetime

    class Config:
        from_attributes = True

class IncidentSchema(BaseModel):
    id: str
    title: str
    event_type: str
    status: str
    road: Optional[str]
    corridor: str
    location_text: str
    lat: Optional[float]
    lon: Optional[float]
    severity: int
    confidence: float
    confidence_breakdown: Dict[str, Any]
    provenance: Dict[str, Any]
    source_count: int
    summary: str
    evidence_quote: Optional[str]
    lifecycle_state: str
    verified_by: Optional[str]
    verification_note: Optional[str]
    created_at: datetime
    updated_at: datetime
    evidence: List[IncidentEvidenceItem] = []

    class Config:
        from_attributes = True

class VerificationRequest(BaseModel):
    decision: Literal["confirm", "reject"]
    note: Optional[str] = None
    verifier: Optional[str] = "Authority Officer"

class RoadSegmentSchema(BaseModel):
    id: str
    edge_id: str
    corridor: str
    road_name: str
    name: str
    start_node: str
    end_node: str
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    coordinates: List[List[float]]
    length_m: float
    base_travel_time_sec: int
    slope_deg: float
    river_proximity_m: float
    landslide_zone: bool
    historical_incident_count: int
    risk_score: float
    risk_label: str
    explanation: Optional[str]

class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]

class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]

class RouteRequest(BaseModel):
    origin: str  # Place name or "lat,lon"
    destination: str  # Place name or "lat,lon"
    preference: Literal["fastest", "safest", "balanced"] = "safest"
    corridor: Optional[str] = "NH-10"

class RouteOption(BaseModel):
    route_id: str
    label: str  # "Safest (Recommended)" | "Fastest" | "Balanced"
    distance_km: float
    eta_minutes: int
    mean_risk: float
    max_risk: float
    risky_segments_count: int
    blocked_segments_count: int
    reason: str
    coordinates: List[List[float]]
    path_nodes: List[str]

class RouteResponse(BaseModel):
    origin: str
    destination: str
    preference: str
    corridor: str
    routes: List[RouteOption]
    rerouted_due_to_incident: bool
    plain_english_advice: str

class RouteCompareResponse(BaseModel):
    corridor: str
    origin: str
    destination: str
    baseline_route: RouteOption
    ridge_route: RouteOption
    risk_reduction_pct: float
    time_difference_minutes: int
    explanation: str

class IngestionRunRequest(BaseModel):
    corridor: str = "NH-10"
    mode: Literal["search", "url"] = "search"
    url: Optional[str] = None

class IngestionStepSchema(BaseModel):
    id: str
    step_name: str
    details: Dict[str, Any]
    timestamp: datetime

    class Config:
        from_attributes = True

class IngestionRunSchema(BaseModel):
    id: str
    corridor: str
    mode: str
    target_url: Optional[str]
    status: str
    new_incidents_count: int
    tinyfish_api_used: str
    duration_ms: int
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    steps: List[IngestionStepSchema] = []

    class Config:
        from_attributes = True

class AlertSchema(BaseModel):
    id: str
    corridor: str
    severity: str
    title: str
    message: str
    incident_id: Optional[str]
    affected_vehicle_ids: List[str]
    suggested_action: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class VehicleSchema(BaseModel):
    id: str
    name: str
    type: str
    corridor: str
    status: str
    current_lat: float
    current_lon: float
    destination: str
    assigned_route_id: Optional[str]
    speed_kmh: float = 38.0
    updated_at: datetime

    class Config:
        from_attributes = True

class DashcamEventSchema(BaseModel):
    id: str
    vehicle_id: str
    hazard_type: str
    corridor: str
    lat: float
    lon: float
    confidence: float
    image_url: Optional[str]
    is_simulated: bool
    incident_id: Optional[str]
    detected_at: datetime

    class Config:
        from_attributes = True

class MetricsSummary(BaseModel):
    active_incidents: int
    verification_queue_count: int
    average_confidence: float
    blocked_segments: int
    routes_rerouted_today: int
    model_accuracy_auc: float
    hotspots: List[Dict[str, Any]]
    incidents_by_type: Dict[str, int]
    incidents_by_corridor: Dict[str, int]
