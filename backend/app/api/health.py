from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.deps import get_db
import os

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # Check if ML model is present
    model_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "models", "risk_xgb.joblib")
    model_loaded = os.path.exists(model_path)

    return {
        "status": "healthy" if db_ok else "degraded",
        "service": "RIDGE Regional Intelligence API",
        "version": "0.1.0",
        "tinyfish_mode": settings.TINYFISH_MODE,
        "tinyfish_configured": bool(settings.TINYFISH_API_KEY),
        "tinyfish_agent_enabled": settings.ENABLE_TINYFISH_AGENT,
        "llm_provider": settings.LLM_PROVIDER,
        "db_ok": db_ok,
        "model_loaded": model_loaded,
        "corridors": ["NH-10 (Siliguri - Gangtok)", "NH-6/27 (Guwahati - Shillong)"]
    }
