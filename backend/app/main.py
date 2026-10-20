from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import (
    health, risk, incidents, gazetteer, metrics,
    ingestion, stream, routes, alerts, fleet, dashcam
)
from app.core.seed import seed_database
from app.core.logging import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Regional Intelligence & Geospatial Efficiency for India's North-Eastern Region",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.API_PREFIX, tags=["Health"])
app.include_router(risk.router, prefix=settings.API_PREFIX, tags=["Risk"])
app.include_router(incidents.router, prefix=settings.API_PREFIX, tags=["Incidents"])
app.include_router(gazetteer.router, prefix=settings.API_PREFIX, tags=["Gazetteer"])
app.include_router(metrics.router, prefix=settings.API_PREFIX, tags=["Metrics"])
app.include_router(ingestion.router, prefix=settings.API_PREFIX, tags=["Ingestion"])
app.include_router(stream.router, prefix=settings.API_PREFIX, tags=["Streaming"])
app.include_router(routes.router, prefix=settings.API_PREFIX, tags=["Routing"])
app.include_router(alerts.router, prefix=settings.API_PREFIX, tags=["Alerts"])
app.include_router(fleet.router, prefix=settings.API_PREFIX, tags=["Fleet"])
app.include_router(dashcam.router, prefix=settings.API_PREFIX, tags=["Dashcam"])

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode")
    logger.info(f"TinyFish Mode: {settings.TINYFISH_MODE} (API Key configured: {bool(settings.TINYFISH_API_KEY)})")
    seed_database()

@app.get("/")
def root():
    return {
        "message": "Welcome to RIDGE API: Regional Intelligence & Geospatial Efficiency",
        "documentation": "/docs",
        "health": f"{settings.API_PREFIX}/health"
    }
