import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.db import Base

def gen_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class Source(Base):
    __tablename__ = "sources"

    id = Column(String(64), primary_key=True, default=gen_uuid)
    domain = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    reliability_tier = Column(String(32), default="established_news")  # official | established_news | social_aggregator | user
    reliability_weight = Column(Float, default=0.75)
    created_at = Column(DateTime, default=utc_now)


class RawDocument(Base):
    __tablename__ = "raw_documents"

    id = Column(String(64), primary_key=True, default=gen_uuid)
    url = Column(Text, index=True, nullable=False)
    domain = Column(String(255), index=True, nullable=False)
    content_hash = Column(String(64), index=True, nullable=False)
    raw_content = Column(Text, nullable=False)
    fetched_at = Column(DateTime, default=utc_now)
    api_endpoint = Column(String(64), default="tinyfish_fetch")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(64), primary_key=True, default=gen_uuid)
    title = Column(String(255), nullable=False)
    event_type = Column(String(64), index=True, nullable=False)  # landslide | flood | waterlogging | road_closed | bridge_damage | accident | restored | other
    status = Column(String(32), index=True, default="blocked")  # blocked | partially_open | open | unknown
    road = Column(String(64), index=True, nullable=True)  # NH-10 | NH-6
    corridor = Column(String(64), index=True, nullable=False)  # NH-10 | NH-6
    location_text = Column(String(255), nullable=False)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    nearest_segment_id = Column(String(64), nullable=True)
    severity = Column(Integer, default=3)  # 1 to 5
    confidence = Column(Float, default=0.5)  # 0.0 to 1.0
    confidence_breakdown = Column(JSON, default=dict)
    provenance = Column(JSON, default=dict)
    source_count = Column(Integer, default=1)
    summary = Column(Text, nullable=False)
    evidence_quote = Column(Text, nullable=True)
    lifecycle_state = Column(String(32), default="active")  # active | monitoring | resolved
    verified_by = Column(String(64), nullable=True)
    verification_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    evidence = relationship("IncidentEvidence", back_populates="incident", cascade="all, delete-orphan")
    verifications = relationship("Verification", back_populates="incident", cascade="all, delete-orphan")


class IncidentEvidence(Base):
    __tablename__ = "incident_evidence"

    id = Column(String(64), primary_key=True, default=gen_uuid)
    incident_id = Column(String(64), ForeignKey("incidents.id"), nullable=False)
    source_url = Column(Text, nullable=False)
    domain = Column(String(255), nullable=False)
    snippet = Column(Text, nullable=False)
    tinyfish_endpoint = Column(String(64), default="search")
    extracted_at = Column(DateTime, default=utc_now)

    incident = relationship("Incident", back_populates="evidence")


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(String(64), primary_key=True, default=gen_uuid)
    incident_id = Column(String(64), ForeignKey("incidents.id"), nullable=False)
    verifier = Column(String(64), default="Authority Officer")
    decision = Column(String(32), nullable=False)  # confirm | reject
    note = Column(Text, nullable=True)
    verified_at = Column(DateTime, default=utc_now)

    incident = relationship("Incident", back_populates="verifications")


class RoadSegment(Base):
    __tablename__ = "road_segments"

    id = Column(String(64), primary_key=True)
    edge_id = Column(String(64), unique=True, index=True, nullable=False)
    corridor = Column(String(64), index=True, nullable=False)
    road_name = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    start_node = Column(String(255), nullable=False)
    end_node = Column(String(255), nullable=False)
    start_lat = Column(Float, nullable=False)
    start_lon = Column(Float, nullable=False)
    end_lat = Column(Float, nullable=False)
    end_lon = Column(Float, nullable=False)
    coordinates_json = Column(JSON, nullable=False)  # [[lon, lat], ...]
    length_m = Column(Float, default=1000.0)
    base_travel_time_sec = Column(Integer, default=120)
    slope_deg = Column(Float, default=5.0)
    river_proximity_m = Column(Float, default=200.0)
    landslide_zone = Column(Boolean, default=False)
    historical_incident_count = Column(Integer, default=0)
    road_class = Column(String(64), default="national_highway")

    risk_score = relationship("RiskScore", back_populates="segment", uselist=False, cascade="all, delete-orphan")


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(String(64), primary_key=True, default=gen_uuid)
    segment_id = Column(String(64), ForeignKey("road_segments.id"), unique=True, nullable=False)
    risk_score = Column(Float, default=0.1)  # 0.0 - 1.0
    risk_label = Column(String(32), default="open")  # open | risky | high_risk | blocked
    explanation = Column(Text, nullable=True)
    features_json = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    segment = relationship("RoadSegment", back_populates="risk_score")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    type = Column(String(64), default="Heavy Freight (16T)")
    corridor = Column(String(64), default="NH-10")
    status = Column(String(32), default="in_transit")  # in_transit | idle | rerouted | alert
    current_lat = Column(Float, nullable=False)
    current_lon = Column(Float, nullable=False)
    destination = Column(String(128), nullable=False)
    assigned_route_id = Column(String(64), nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class VehiclePosition(Base):
    __tablename__ = "vehicle_positions"

    id = Column(String(64), primary_key=True, default=gen_uuid)
    vehicle_id = Column(String(64), ForeignKey("vehicles.id"), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    speed_kmh = Column(Float, default=35.0)
    recorded_at = Column(DateTime, default=utc_now)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(64), primary_key=True, default=gen_uuid)
    corridor = Column(String(64), index=True, nullable=False)
    severity = Column(String(32), default="high")  # low | medium | high | critical
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    incident_id = Column(String(64), nullable=True)
    affected_vehicle_ids = Column(JSON, default=list)
    suggested_action = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = Column(String(64), primary_key=True, default=gen_uuid)
    corridor = Column(String(64), nullable=False)
    mode = Column(String(32), default="search")  # search | url
    target_url = Column(Text, nullable=True)
    status = Column(String(32), default="running")  # running | completed | failed
    new_incidents_count = Column(Integer, default=0)
    tinyfish_api_used = Column(String(64), default="Search + Fetch")
    duration_ms = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)

    steps = relationship("IngestionStep", back_populates="run", cascade="all, delete-orphan")


class IngestionStep(Base):
    __tablename__ = "ingestion_steps"

    id = Column(String(64), primary_key=True, default=gen_uuid)
    run_id = Column(String(64), ForeignKey("ingestion_runs.id"), nullable=False)
    step_name = Column(String(64), nullable=False)  # search_started | results_found | fetch_done | extracted | geocoded | incident_created
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=utc_now)

    run = relationship("IngestionRun", back_populates="steps")


class DashcamEvent(Base):
    __tablename__ = "dashcam_events"

    id = Column(String(64), primary_key=True, default=gen_uuid)
    vehicle_id = Column(String(64), nullable=False)
    hazard_type = Column(String(64), nullable=False)  # rockfall | pothole | debris | waterlogging
    corridor = Column(String(64), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    confidence = Column(Float, default=0.85)
    image_url = Column(Text, nullable=True)
    is_simulated = Column(Boolean, default=True)
    incident_id = Column(String(64), nullable=True)
    detected_at = Column(DateTime, default=utc_now)
