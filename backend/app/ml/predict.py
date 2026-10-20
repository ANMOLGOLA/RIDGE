import os
import json
import joblib
import pandas as pd
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.models import RoadSegment, RiskScore, Incident
from app.ml.features import FEATURE_NAMES, extract_segment_features
from app.ml.explain import generate_plain_english_explanation
from app.core.logging import logger

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "models", "risk_xgb.joblib")
WEATHER_FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "fixtures", "weather.json")

class RiskPredictor:
    def __init__(self):
        self.model = None
        self._load_model()
        self._load_weather()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                logger.info("XGBoost Risk Model successfully loaded.")
            except Exception as e:
                logger.warning(f"Could not load XGBoost model: {e}")

    def _load_weather(self):
        self.weather = {}
        if os.path.exists(WEATHER_FIXTURE_PATH):
            try:
                with open(WEATHER_FIXTURE_PATH, "r", encoding="utf-8") as f:
                    self.weather = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load weather fixture: {e}")

    def score_all_segments(self, db: Session):
        """
        Calculates and saves risk scores for all road segments in the database.
        Forces 'blocked' for any segment with an active confirmed blockage.
        """
        segments = db.query(RoadSegment).all()
        # Find all active incidents
        active_incidents = db.query(Incident).filter(Incident.lifecycle_state == "active").all()
        blocked_seg_ids = {
            inc.nearest_segment_id: inc
            for inc in active_incidents
            if inc.status == "blocked" and inc.nearest_segment_id
        }

        for seg in segments:
            # 1. Check if forced blocked by live confirmed incident
            if seg.id in blocked_seg_ids:
                inc = blocked_seg_ids[seg.id]
                score = 1.0
                label = "blocked"
                explanation = f"Blocked by live confirmed incident: {inc.title}"
                feat_dict = {}
            else:
                # 2. Extract features
                corridor_weather = self.weather.get(seg.corridor, {})
                live_nearby = sum(1 for i in active_incidents if i.nearest_segment_id == seg.id)
                feat_dict = extract_segment_features(
                    segment_data={
                        "slope_deg": seg.slope_deg,
                        "river_proximity_m": seg.river_proximity_m,
                        "landslide_zone": seg.landslide_zone,
                        "historical_incident_count": seg.historical_incident_count
                    },
                    weather_data=corridor_weather,
                    live_incidents_count=live_nearby
                )

                if self.model:
                    df = pd.DataFrame([feat_dict])[FEATURE_NAMES]
                    proba = float(self.model.predict_proba(df)[0, 1])
                    score = round(proba, 2)
                else:
                    # Fallback rule-based score
                    score = 0.65 if seg.landslide_zone else 0.15

                # Assign label
                if score >= 0.65:
                    label = "high_risk"
                elif score >= 0.35:
                    label = "risky"
                else:
                    label = "open"

                explanation = generate_plain_english_explanation(feat_dict, score)

            # Update or create RiskScore
            risk_entry = db.query(RiskScore).filter(RiskScore.segment_id == seg.id).first()
            if not risk_entry:
                risk_entry = RiskScore(segment_id=seg.id)
                db.add(risk_entry)

            risk_entry.risk_score = score
            risk_entry.risk_label = label
            risk_entry.explanation = explanation
            risk_entry.features_json = feat_dict

        db.commit()
        logger.info(f"Updated risk scores for {len(segments)} segments.")

risk_predictor = RiskPredictor()
