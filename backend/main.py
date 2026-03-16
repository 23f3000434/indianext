import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import url_scan, email_scan, prompt_scan, behavior_scan
from ml.model_trainer import train_all_models

app = FastAPI(
    title="SaveWaves API",
    description="Intelligent Cyber Threat Detection Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Train models on startup if not already trained."""
    train_all_models()

app.include_router(url_scan.router, prefix="/api/scan", tags=["URL Scanner"])
app.include_router(email_scan.router, prefix="/api/scan", tags=["Email Scanner"])
app.include_router(prompt_scan.router, prefix="/api/scan", tags=["Prompt Injection"])
app.include_router(behavior_scan.router, prefix="/api/scan", tags=["Behavior Anomaly"])

@app.get("/")
def root():
    return {"status": "SaveWaves API is running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}