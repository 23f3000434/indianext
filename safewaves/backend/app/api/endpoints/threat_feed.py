"""
GET /threat-feed -- Aggregated threat feed endpoint.
GET /threat-feed/stream -- SSE real-time threat stream.
GET /threat-feed/stats -- Aggregate stats.
"""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from app.models.schemas import ThreatFeedResponse
from app.services.threat_store import threat_store

router = APIRouter()


@router.get("/threat-feed", response_model=ThreatFeedResponse)
async def get_threat_feed():
    threats = threat_store.get_all()
    return ThreatFeedResponse(
        threats=threats,
        total=len(threats),
    )


@router.get("/threat-feed/stats")
async def get_threat_stats():
    return threat_store.get_stats()


@router.get("/threat-feed/stream")
async def threat_stream():
    """Server-Sent Events stream for real-time threat alerts."""
    async def event_generator():
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def on_threat(threat):
            loop.call_soon_threadsafe(queue.put_nowait, threat)

        threat_store.subscribe(on_threat)
        try:
            # Send initial keepalive
            yield f"event: connected\ndata: {json.dumps({'status': 'connected'})}\n\n"

            while True:
                try:
                    threat = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"event: threat\ndata: {json.dumps(threat)}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive ping every 15s
                    yield f"event: ping\ndata: {json.dumps({'type': 'keepalive'})}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            threat_store.unsubscribe(on_threat)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
