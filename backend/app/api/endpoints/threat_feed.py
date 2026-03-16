"""
GET /threat-feed -- Aggregated threat feed endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter

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
