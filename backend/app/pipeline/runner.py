import asyncio
import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.models import (
    IngestionRun, IngestionStep, Incident, IncidentEvidence,
    RoadSegment, RiskScore, Alert
)
from app.core.events import pipeline_broadcaster, alert_broadcaster
from app.pipeline.discover import discover_candidates
from app.pipeline.fetch import fetch_contents
from app.pipeline.extract import extract_event
from app.pipeline.geocode import geocode_location
from app.pipeline.dedupe import find_duplicate_incident
from app.pipeline.confidence import calculate_confidence
from app.core.logging import logger

async def run_ingestion_pipeline(
    db: Session,
    corridor: str = "NH-10",
    mode: str = "search",
    target_url: str = None
) -> IngestionRun:
    """
    Orchestrates the full end-to-end TinyFish web intelligence pipeline:
    1. search_started: TinyFish Search query triggered
    2. results_found: Candidate URLs discovered
    3. fetch_done: Pages rendered and scraped clean via TinyFish Fetch
    4. extracted: Events structured with Pydantic validation
    5. geocoded: Landmark snapped via Gazetteer + RapidFuzz
    6. incident_created: Saved to PostGIS/SQLite, confidence breakdown logged, SSE emitted
    """
    start_time = time.time()
    now = datetime.now(timezone.utc)

    run = IngestionRun(
        corridor=corridor,
        mode=mode,
        target_url=target_url,
        status="running",
        tinyfish_api_used="Search + Fetch" if mode == "search" else "Direct Fetch",
        started_at=now
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    async def log_step(name: str, details: dict):
        step = IngestionStep(
            run_id=run.id,
            step_name=name,
            details=details,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(step)
        db.commit()
        await pipeline_broadcaster.broadcast(name, {
            "run_id": run.id,
            "step": name,
            "corridor": corridor,
            **details
        })

    try:
        # Step 1: Search / Discover
        await log_step("search_started", {
            "mode": mode,
            "target": target_url if mode == "url" else f"{corridor} advisories"
        })

        candidates = []
        if mode == "url" and target_url:
            domain = target_url.split("/")[2] if "//" in target_url else "web"
            candidates = [{
                "title": f"Live Web Advisory ({domain})",
                "url": target_url,
                "snippet": "User pasted live road advisory bulletin.",
                "corridor": corridor
            }]
        else:
            candidates = discover_candidates(corridor)

        await log_step("results_found", {
            "count": len(candidates),
            "urls": [c["url"] for c in candidates[:4]]
        })

        # Step 2: Fetch clean contents
        urls_to_fetch = [c["url"] for c in candidates[:3]]
        fetched_pages = fetch_contents(urls_to_fetch)

        await log_step("fetch_done", {
            "fetched_count": len(fetched_pages),
            "hashes": [p.get("content_hash", "")[:8] for p in fetched_pages]
        })

        # Step 3: Extract & Geocode each page
        created_incidents_count = 0

        for page in fetched_pages:
            url = page["url"]
            domain = url.split("/")[2] if "//" in url else "unknown"
            content = page.get("content", "")
            if not content:
                continue

            # Extract
            extracted = extract_event(content, title="", corridor=corridor)
            await log_step("extracted", {
                "event_type": extracted.event_type,
                "status": extracted.status,
                "location_text": extracted.location_text,
                "severity": extracted.severity,
                "quote": extracted.evidence_quote
            })

            # Geocode
            lat, lon, nearest_seg_id, precision = geocode_location(extracted.location_text, corridor)
            await log_step("geocoded", {
                "location_text": extracted.location_text,
                "lat": lat,
                "lon": lon,
                "nearest_segment_id": nearest_seg_id,
                "precision": precision
            })

            # Dedupe & Confidence
            existing = find_duplicate_incident(db, corridor, extracted.event_type, lat, lon)
            confidence, breakdown = calculate_confidence(
                domain=domain,
                source_count=(existing.source_count + 1) if existing else 1,
                geocoding_precision=precision
            )

            if existing:
                # Corroborate existing incident
                existing.source_count += 1
                existing.confidence = min(1.0, existing.confidence + 0.15)
                existing.updated_at = datetime.now(timezone.utc)
                db.commit()
                inc_id = existing.id
            else:
                # Create new Incident
                incident = Incident(
                    title=f"{extracted.event_type.replace('_', ' ').capitalize()} at {extracted.location_text}",
                    event_type=extracted.event_type,
                    status=extracted.status,
                    road=extracted.road or corridor,
                    corridor=corridor,
                    location_text=extracted.location_text,
                    lat=lat,
                    lon=lon,
                    nearest_segment_id=nearest_seg_id,
                    severity=extracted.severity,
                    confidence=confidence,
                    confidence_breakdown=breakdown,
                    provenance={
                        "source_url": url,
                        "domain": domain,
                        "tinyfish_api": "api.fetch.tinyfish.ai",
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                        "content_hash": page.get("content_hash", "")
                    },
                    source_count=1,
                    summary=extracted.summary,
                    evidence_quote=extracted.evidence_quote,
                    lifecycle_state="active" if extracted.status != "open" else "resolved"
                )
                db.add(incident)
                db.commit()
                db.refresh(incident)
                inc_id = incident.id
                created_incidents_count += 1

                # Add evidence
                ev = IncidentEvidence(
                    incident_id=inc_id,
                    source_url=url,
                    domain=domain,
                    snippet=extracted.evidence_quote,
                    tinyfish_endpoint="fetch"
                )
                db.add(ev)

                # If blocked or high risk, update segment risk score
                if nearest_seg_id:
                    seg_risk = db.query(RiskScore).filter(RiskScore.segment_id == nearest_seg_id).first()
                    if seg_risk:
                        if extracted.status == "blocked":
                            seg_risk.risk_score = 1.0
                            seg_risk.risk_label = "blocked"
                            seg_risk.explanation = f"Blocked by live TinyFish incident: {extracted.summary}"
                        elif extracted.status == "partially_open":
                            seg_risk.risk_score = max(seg_risk.risk_score, 0.68)
                            seg_risk.risk_label = "high_risk"
                            seg_risk.explanation = f"Single lane traffic: {extracted.summary}"

                # Create Alert for critical / blocked incidents
                if extracted.status == "blocked" or extracted.severity >= 4:
                    alert = Alert(
                        corridor=corridor,
                        severity="critical" if extracted.status == "blocked" else "high",
                        title=f"{corridor} Alert: {extracted.event_type.capitalize()} at {extracted.location_text}",
                        message=extracted.summary,
                        incident_id=inc_id,
                        suggested_action="Dynamic reroute recommended. Avoid this segment."
                    )
                    db.add(alert)
                    db.commit()
                    db.refresh(alert)
                    await alert_broadcaster.broadcast("alert_created", {
                        "id": alert.id,
                        "corridor": alert.corridor,
                        "severity": alert.severity,
                        "title": alert.title,
                        "message": alert.message,
                        "suggested_action": alert.suggested_action,
                        "created_at": alert.created_at.isoformat()
                    })

            await log_step("incident_created", {
                "incident_id": inc_id,
                "title": extracted.summary,
                "confidence": confidence,
                "status": extracted.status,
                "is_corroborated": bool(existing)
            })

        duration_ms = int((time.time() - start_time) * 1000)
        run.status = "completed"
        run.new_incidents_count = created_incidents_count
        run.duration_ms = duration_ms
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(run)

        logger.info(f"Ingestion Run {run.id} completed successfully in {duration_ms}ms")
        return run

    except Exception as e:
        logger.error(f"Ingestion Run failed: {e}")
        run.status = "failed"
        run.error_message = str(e)
        run.duration_ms = int((time.time() - start_time) * 1000)
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        raise
