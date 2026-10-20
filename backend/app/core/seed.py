import json
import os
from datetime import datetime, timezone, timedelta
from app.core.db import Base, engine, SessionLocal
from app.core.models import (
    Source, RoadSegment, RiskScore, Incident, IncidentEvidence,
    Vehicle, Alert, IngestionRun, IngestionStep
)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(RoadSegment).count() > 0:
            print("Database already contains road segments. Skipping segment seed.")
            return

        print("Seeding database tables...")

        # 1. Sources
        sources = [
            Source(id="src_1", domain="sikkimexpress.com", name="Sikkim Express", reliability_tier="established_news", reliability_weight=0.88),
            Source(id="src_2", domain="eastmojo.com", name="EastMojo", reliability_tier="established_news", reliability_weight=0.85),
            Source(id="src_3", domain="themeghalayan.com", name="The Meghalayan", reliability_tier="established_news", reliability_weight=0.84),
            Source(id="src_4", domain="morungexpress.com", name="The Morung Express", reliability_tier="established_news", reliability_weight=0.82),
            Source(id="src_5", domain="sentinelassam.com", name="The Sentinel Assam", reliability_tier="established_news", reliability_weight=0.86),
            Source(id="src_6", domain="sikkim.gov.in", name="Government of Sikkim Disaster Management", reliability_tier="official", reliability_weight=0.98),
            Source(id="src_7", domain="meghalaya.gov.in", name="Meghalaya State Disaster Management Authority", reliability_tier="official", reliability_weight=0.98),
        ]
        db.add_all(sources)

        # 2. Road Segments & Default Risk Scores
        corridors_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "corridors.json")
        with open(corridors_file, "r", encoding="utf-8") as f:
            segments_data = json.load(f)

        now = datetime.now(timezone.utc)
        for s in segments_data:
            segment = RoadSegment(
                id=s["id"],
                edge_id=s["edge_id"],
                corridor=s["corridor"],
                road_name=s["road_name"],
                name=s["name"],
                start_node=s["start_node"],
                end_node=s["end_node"],
                start_lat=s["start_lat"],
                start_lon=s["start_lon"],
                end_lat=s["end_lat"],
                end_lon=s["end_lon"],
                coordinates_json=s["geometry"]["coordinates"],
                length_m=s["length_m"],
                base_travel_time_sec=s["base_travel_time_sec"],
                slope_deg=s["slope_deg"],
                river_proximity_m=s["river_proximity_m"],
                landslide_zone=s["landslide_zone"],
                historical_incident_count=s["historical_incident_count"],
                road_class=s["road_class"]
            )
            db.add(segment)

            # Default initial risk score
            base_risk = 0.12
            if s["landslide_zone"]:
                base_risk = 0.58
            if s["slope_deg"] > 20:
                base_risk = min(0.85, base_risk + 0.15)
            
            label = "open"
            if base_risk > 0.65:
                label = "high_risk"
            elif base_risk >= 0.35:
                label = "risky"

            risk = RiskScore(
                segment_id=s["id"],
                risk_score=round(base_risk, 2),
                risk_label=label,
                explanation=f"Steep slope ({s['slope_deg']}°) & river proximity ({s['river_proximity_m']}m)" if s["landslide_zone"] else "Normal baseline conditions",
                features_json={
                    "slope_deg": s["slope_deg"],
                    "river_proximity_m": s["river_proximity_m"],
                    "historical_frequency": s["historical_incident_count"]
                }
            )
            db.add(risk)

        db.commit()
        print(f"Inserted {len(segments_data)} road segments and risk scores.")

        # 3. Seed Realistic Incidents
        advisories_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "fixtures", "advisories.json")
        with open(advisories_file, "r", encoding="utf-8") as f:
            advs = json.load(f)

        # Seed the top 5 key incidents
        seed_advs = advs[:6]
        for a in seed_advs:
            exp = a["expected_event"]
            # Find nearest segment
            seg_match = db.query(RoadSegment).filter(RoadSegment.corridor == a["corridor"]).first()
            if a["id"] == "adv_001":
                # 29th mile on NH-10
                seg_match = db.query(RoadSegment).filter(RoadSegment.id == "seg_nh10_011").first() or seg_match
                inc_lat, inc_lon = 27.0450, 88.4320
                conf = 0.92
                status = "blocked"
            elif a["id"] == "adv_002":
                # Kalijhora on NH-10
                seg_match = db.query(RoadSegment).filter(RoadSegment.id == "seg_nh10_006").first() or seg_match
                inc_lat, inc_lon = 26.9324, 88.4552
                conf = 0.81
                status = "partially_open"
            elif a["id"] == "adv_003":
                # Jorabat on NH-6
                seg_match = db.query(RoadSegment).filter(RoadSegment.id == "seg_nh6_004").first() or seg_match
                inc_lat, inc_lon = 26.0967, 91.8702
                conf = 0.86
                status = "partially_open"
            elif a["id"] == "adv_004":
                # Barapani on NH-6
                seg_match = db.query(RoadSegment).filter(RoadSegment.id == "seg_nh6_014").first() or seg_match
                inc_lat, inc_lon = 25.6542, 91.9158
                conf = 0.76
                status = "partially_open"
            else:
                inc_lat = seg_match.start_lat if seg_match else 27.10
                inc_lon = seg_match.start_lon if seg_match else 88.50
                conf = 0.44  # This one goes to verification queue!
                status = exp["status"]

            inc = Incident(
                id=f"inc_{a['id']}",
                title=a["title"],
                event_type=exp["event_type"],
                status=status,
                road=exp["road"],
                corridor=a["corridor"],
                location_text=exp["location_text"],
                lat=inc_lat,
                lon=inc_lon,
                nearest_segment_id=seg_match.id if seg_match else None,
                severity=exp["severity"],
                confidence=conf,
                confidence_breakdown={
                    "source_reliability": 0.88,
                    "corroboration_count": 2 if conf > 0.8 else 1,
                    "geocoding_precision": 0.95,
                    "recency_decay": 0.90
                },
                provenance={
                    "source_url": a["url"],
                    "domain": a["url"].split("/")[2],
                    "tinyfish_api": "api.search.tinyfish.ai + api.fetch.tinyfish.ai",
                    "fetched_at": a["published_at"],
                    "content_hash": "sha256_mock_hash_" + a["id"]
                },
                source_count=2 if conf > 0.8 else 1,
                summary=a["text"][:160] + "...",
                evidence_quote=exp["evidence_quote"],
                lifecycle_state="active" if status != "open" else "resolved",
                created_at=datetime.fromisoformat(a["published_at"])
            )
            db.add(inc)

            # Add evidence record
            ev = IncidentEvidence(
                incident_id=inc.id,
                source_url=a["url"],
                domain=a["url"].split("/")[2],
                snippet=exp["evidence_quote"],
                tinyfish_endpoint="fetch",
                extracted_at=datetime.fromisoformat(a["published_at"])
            )
            db.add(ev)

            # If blocked, update the corresponding segment's risk score to blocked!
            if status == "blocked" and seg_match:
                risk_entry = db.query(RiskScore).filter(RiskScore.segment_id == seg_match.id).first()
                if risk_entry:
                    risk_entry.risk_score = 1.0
                    risk_entry.risk_label = "blocked"
                    risk_entry.explanation = f"Blocked by active incident: {a['title']}"

        # 4. Seed Vehicles
        vehicles = [
            Vehicle(
                id="veh_nh10_01",
                name="Freightliner TR-101 (Medicine & Supplies)",
                type="Heavy Freight (16T)",
                corridor="NH-10",
                status="in_transit",
                current_lat=26.8845,
                current_lon=88.4727,
                destination="Gangtok Central Depot"
            ),
            Vehicle(
                id="veh_nh10_02",
                name="ColdChain Van CC-204 (Perishables)",
                type="Refrigerated Van (3.5T)",
                corridor="NH-10",
                status="rerouted",
                current_lat=27.0864,
                current_lon=88.4542,
                destination="Ranipool Logistics Hub"
            ),
            Vehicle(
                id="veh_nh6_01",
                name="Assam-Meghalaya Carrier AM-88",
                type="Container Truck (24T)",
                corridor="NH-6",
                status="in_transit",
                current_lat=25.9038,
                current_lon=91.8814,
                destination="Shillong Police Bazar"
            ),
            Vehicle(
                id="veh_nh6_02",
                name="Express Delivery EX-402",
                type="Light Commercial Vehicle (LCV)",
                corridor="NH-6",
                status="in_transit",
                current_lat=26.0967,
                current_lon=91.8702,
                destination="Umiam Industrial Hub"
            )
        ]
        db.add_all(vehicles)

        # 5. Seed Initial Alerts
        alerts = [
            Alert(
                id="alt_001",
                corridor="NH-10",
                severity="critical",
                title="NH-10 Blockage at 29th Mile",
                message="Massive landslide has cut off NH-10 near 29th Mile. Automatic rerouting calculated via Gorubathan / Lava.",
                incident_id="inc_adv_001",
                affected_vehicle_ids=["veh_nh10_01", "veh_nh10_02"],
                suggested_action="Divert fleet via Lava/Reshi or pause at Sevoke until clearance."
            ),
            Alert(
                id="alt_002",
                corridor="NH-6",
                severity="high",
                title="Waterlogging Alert at Jorabat",
                message="Knee-deep waterlogging on NH-6 tri-junction slows inbound freight. Expect +35 min transit delay.",
                incident_id="inc_adv_003",
                affected_vehicle_ids=["veh_nh6_02"],
                suggested_action="Shift to right lane or delay departure by 45 minutes."
            )
        ]
        db.add_all(alerts)

        # 6. Seed Ingestion Run history
        run = IngestionRun(
            id="run_init_001",
            corridor="NH-10",
            mode="search",
            status="completed",
            new_incidents_count=2,
            tinyfish_api_used="Search + Fetch",
            duration_ms=1840,
            started_at=now - timedelta(minutes=45),
            completed_at=now - timedelta(minutes=44)
        )
        db.add(run)

        db.commit()
        print("Database successfully seeded with realistic RIDGE data!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
