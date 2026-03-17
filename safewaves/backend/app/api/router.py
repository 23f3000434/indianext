"""
safewaves API Router
=====================
Main API router that includes all endpoint routers.
"""

from fastapi import APIRouter

from app.api.endpoints import (
    email,
    url,
    deepfake,
    prompt,
    behavior,
    ai_content,
    threat_feed,
    adversarial,
    fusion,
)

router = APIRouter()

router.include_router(email.router, prefix="/analyze", tags=["Analysis"])
router.include_router(url.router, prefix="/analyze", tags=["Analysis"])
router.include_router(deepfake.router, prefix="/analyze", tags=["Analysis"])
router.include_router(prompt.router, prefix="/analyze", tags=["Analysis"])
router.include_router(behavior.router, prefix="/analyze", tags=["Analysis"])
router.include_router(ai_content.router, prefix="/analyze", tags=["Analysis"])
router.include_router(threat_feed.router, tags=["Threat Feed"])
router.include_router(adversarial.router, tags=["Adversarial Testing"])
router.include_router(fusion.router, tags=["Threat Fusion"])
