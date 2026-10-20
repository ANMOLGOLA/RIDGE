from typing import Dict, Any, List

FEATURE_NAMES = [
    "rain_past_24h_mm",
    "rain_forecast_24h_mm",
    "slope_deg",
    "river_proximity_m",
    "landslide_zone",
    "historical_incident_count",
    "live_incidents_nearby",
    "season_monsoon"
]

def extract_segment_features(
    segment_data: Dict[str, Any],
    weather_data: Dict[str, Any],
    live_incidents_count: int = 0
) -> Dict[str, float]:
    """
    Extracts numerical feature vector for the XGBoost risk model.
    """
    past_rain = weather_data.get("hourly", {}).get("precipitation_past_24h_mm", 45.0)
    forecast_rain = weather_data.get("hourly", {}).get("precipitation_forecast_24h_mm", 55.0)

    slope = float(segment_data.get("slope_deg", 8.0))
    river_prox = float(segment_data.get("river_proximity_m", 250.0))
    landslide_zone = 1.0 if segment_data.get("landslide_zone", False) else 0.0
    hist_inc = float(segment_data.get("historical_incident_count", 2))

    return {
        "rain_past_24h_mm": past_rain,
        "rain_forecast_24h_mm": forecast_rain,
        "slope_deg": slope,
        "river_proximity_m": river_prox,
        "landslide_zone": landslide_zone,
        "historical_incident_count": hist_inc,
        "live_incidents_nearby": float(live_incidents_count),
        "season_monsoon": 1.0  # Monsoonal conditions
    }
