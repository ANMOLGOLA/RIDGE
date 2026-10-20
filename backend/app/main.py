from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import health
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

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode")
    logger.info(f"TinyFish Mode: {settings.TINYFISH_MODE} (API Key configured: {bool(settings.TINYFISH_API_KEY)})")

@app.get("/")
def root():
    return {
        "message": "Welcome to RIDGE API: Regional Intelligence & Geospatial Efficiency",
        "documentation": "/docs",
        "health": f"{settings.API_PREFIX}/health"
    }
