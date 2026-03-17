import time
from collections import defaultdict
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("safewaves API starting...")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Rate Limiting Middleware ──────────────────────────────
class RateLimiter:
    """Simple in-memory sliding window rate limiter."""

    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - 60.0

        # Clean old entries
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if t > window_start
        ]

        if len(self.requests[client_ip]) >= self.rpm:
            return False

        self.requests[client_ip].append(now)
        return True

    def remaining(self, client_ip: str) -> int:
        now = time.time()
        window_start = now - 60.0
        recent = [t for t in self.requests.get(client_ip, []) if t > window_start]
        return max(0, self.rpm - len(recent))


_rate_limiter = RateLimiter(requests_per_minute=60)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for docs, health, and SSE stream
    path = request.url.path
    if path in ("/docs", "/openapi.json", "/health", "/", "/redoc"):
        return await call_next(request)
    if path.endswith("/stream"):
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"

    if not _rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Max 60 requests per minute."},
            headers={"Retry-After": "60"},
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(
        _rate_limiter.remaining(client_ip)
    )
    return response


app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}


@app.get("/")
async def root():
    return {"message": "safewaves API", "docs": "/docs"}
