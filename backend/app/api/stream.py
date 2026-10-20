import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.core.events import pipeline_broadcaster, alert_broadcaster

router = APIRouter(prefix="/stream", tags=["Streaming"])

@router.get("/pipeline")
async def stream_pipeline():
    """
    Server-Sent Events (SSE) stream broadcasting each stage of the TinyFish web intelligence pipeline:
    search_started -> results_found -> fetch_done -> extracted -> geocoded -> incident_created
    """
    queue = pipeline_broadcaster.subscribe()

    async def event_generator():
        try:
            # Send initial keepalive
            yield f"event: connected\ndata: {json.dumps({'message': 'Connected to RIDGE TinyFish pipeline stream'})}\n\n"
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=25.0)
                    yield f"event: {msg['event']}\ndata: {json.dumps(msg['data'])}\n\n"
                except asyncio.TimeoutError:
                    # Keepalive ping
                    yield "event: ping\ndata: {}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            pipeline_broadcaster.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/alerts")
async def stream_alerts():
    """
    Server-Sent Events (SSE) stream broadcasting real-time corridor alerts & dynamic reroute updates.
    """
    queue = alert_broadcaster.subscribe()

    async def event_generator():
        try:
            yield f"event: connected\ndata: {json.dumps({'message': 'Connected to RIDGE Live Alerts stream'})}\n\n"
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=25.0)
                    yield f"event: {msg['event']}\ndata: {json.dumps(msg['data'])}\n\n"
                except asyncio.TimeoutError:
                    yield "event: ping\ndata: {}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            alert_broadcaster.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
