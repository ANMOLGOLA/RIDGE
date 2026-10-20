from typing import Dict, Any, Tuple

def calculate_confidence(
    domain: str,
    source_count: int,
    geocoding_precision: float,
    hours_ago: float = 0.5
) -> Tuple[float, Dict[str, Any]]:
    """
    Step 5: Multi-factor confidence calculation (0 to 1).
    Factors:
    1. Source Reliability (35%)
    2. Corroboration / Source Count (25%)
    3. Geocoding Precision (25%)
    4. Recency Decay (15%)
    """
    # 1. Source Reliability
    d_lower = domain.lower()
    if any(gov in d_lower for gov in [".gov.in", "police", "ndma", "sdma", "bro."]):
        source_rel = 0.98
    elif any(news in d_lower for news in ["sikkimexpress", "eastmojo", "themeghalayan", "sentinel", "morung", "thehindu", "ndtv"]):
        source_rel = 0.88
    else:
        source_rel = 0.65

    # 2. Corroboration Count
    if source_count >= 3:
        corrob = 1.0
    elif source_count == 2:
        corrob = 0.85
    else:
        corrob = 0.65

    # 3. Geocoding Precision
    geo_prec = max(0.4, min(1.0, geocoding_precision))

    # 4. Recency Decay (Linear decay over 24 hours, down to 0.5)
    recency = max(0.5, 1.0 - (hours_ago / 48.0))

    # Combined score
    confidence = (
        0.35 * source_rel +
        0.25 * corrob +
        0.25 * geo_prec +
        0.15 * recency
    )
    confidence = round(min(1.0, max(0.1, confidence)), 2)

    breakdown = {
        "source_reliability": round(source_rel, 2),
        "corroboration_count": round(corrob, 2),
        "geocoding_precision": round(geo_prec, 2),
        "recency_decay": round(recency, 2)
    }

    return confidence, breakdown
