import random
from datetime import datetime, timezone
from typing import List, Dict, Any

SIMULATED_HAZARDS = [
    {
        "hazard_type": "rockfall",
        "corridor": "NH-10",
        "lat": 26.9850,
        "lon": 88.4360,
        "location": "Birik Dara Curve",
        "confidence": 0.94,
        "image_url": "https://images.unsplash.com/photo-1541888946425-d0fbb18f156b?auto=format&fit=crop&w=600&q=80"
    },
    {
        "hazard_type": "waterlogging",
        "corridor": "NH-6",
        "lat": 26.0463,
        "lon": 91.8647,
        "location": "Byrnihat Commercial Area",
        "confidence": 0.88,
        "image_url": "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?auto=format&fit=crop&w=600&q=80"
    },
    {
        "hazard_type": "debris",
        "corridor": "NH-10",
        "lat": 27.1210,
        "lon": 88.4850,
        "location": "Tarkhola Crossing",
        "confidence": 0.91,
        "image_url": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=600&q=80"
    },
    {
        "hazard_type": "pothole",
        "corridor": "NH-6",
        "lat": 25.7512,
        "lon": 91.8856,
        "location": "Umsning Expressway Bypass",
        "confidence": 0.85,
        "image_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80"
    }
]

def generate_simulated_dashcam_event(vehicle_id: str = "veh_nh10_01") -> Dict[str, Any]:
    hazard = random.choice(SIMULATED_HAZARDS)
    return {
        "vehicle_id": vehicle_id,
        "hazard_type": hazard["hazard_type"],
        "corridor": hazard["corridor"],
        "lat": hazard["lat"] + random.uniform(-0.002, 0.002),
        "lon": hazard["lon"] + random.uniform(-0.002, 0.002),
        "location_text": hazard["location"],
        "confidence": hazard["confidence"],
        "image_url": hazard["image_url"],
        "is_simulated": True,
        "detected_at": datetime.now(timezone.utc)
    }
