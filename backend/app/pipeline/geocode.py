import os
import json
import math
from typing import Tuple, Optional, Dict, Any
from rapidfuzz import process, fuzz
from app.core.logging import logger

GAZETTEER_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "gazetteer.json")
CORRIDORS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "corridors.json")

def load_gazetteer():
    if os.path.exists(GAZETTEER_FILE):
        with open(GAZETTEER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_segments():
    if os.path.exists(CORRIDORS_FILE):
        with open(CORRIDORS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def haversine_dist(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000  # meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def geocode_location(location_text: str, corridor: str = "NH-10") -> Tuple[Optional[float], Optional[float], Optional[str], float]:
    """
    Step 4: Geocode extracted location text.
    Fuzzy matches place names and aliases against the bundled Gazetteer and snaps to nearest segment.
    Returns (lat, lon, nearest_segment_id, precision_score).
    """
    gaz = load_gazetteer()
    segments = load_segments()
    if not gaz:
        return None, None, None, 0.0

    # Filter gazetteer entries for the corridor first, fallback to all
    corridor_gaz = [g for g in gaz if g.get("corridor") == corridor] or gaz

    # Build corpus of names and aliases
    candidates = {}
    for g in corridor_gaz:
        candidates[g["name"].lower()] = g
        for alias in g.get("aliases", []):
            candidates[alias.lower()] = g

    # Fuzzy match
    match, score, _ = process.extractOne(
        location_text.lower(),
        list(candidates.keys()),
        scorer=fuzz.WRatio
    )

    if score < 50:
        logger.warning(f"Low geocode confidence ({score}%) for: '{location_text}'")
        # Return fallback corridor midpoint
        if corridor == "NH-10":
            return 27.05, 88.45, "seg_nh10_011", 0.50
        else:
            return 25.85, 91.88, "seg_nh6_008", 0.50

    matched_place = candidates[match]
    lat, lon = matched_place["lat"], matched_place["lon"]
    precision = min(1.0, score / 100.0)

    # Snap to nearest segment
    nearest_seg_id = None
    min_dist = float("inf")
    for s in segments:
        if s.get("corridor") == corridor:
            d = haversine_dist(lat, lon, s["start_lat"], s["start_lon"])
            if d < min_dist:
                min_dist = d
                nearest_seg_id = s["id"]

    return lat, lon, nearest_seg_id, precision
