import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.core.schemas import ExtractedEvent
from app.config import settings
from app.core.logging import logger

EVENT_KEYWORDS = {
    "landslide": ["landslide", "landslip", "rockfall", "mudslide", "shooting stones", "debris", "boulders"],
    "flood": ["flood", "submerged", "inundated", "river breached", "overflowing", "washed away"],
    "waterlogging": ["waterlogging", "waterlogged", "knee-deep water", "puddles", "water accumulation"],
    "bridge_damage": ["bridge collapse", "bridge damage", "pier damage", "causeway damaged", "spillway"],
    "accident": ["accident", "overturned", "collision", "trailer overturned", "tanker"],
    "restored": ["restored", "reopened", "cleared", "traffic resumed", "normal traffic", "debris removed"],
    "road_closed": ["road closed", "traffic suspended", "halted", "closed for traffic", "diversion", "subsidence"]
}

STATUS_KEYWORDS = {
    "blocked": ["blocked", "closed", "suspended", "halted", "cut off", "standstill", "washed away", "impassable"],
    "partially_open": ["partially", "single-lane", "single lane", "one-way", "crawls", "slow-moving", "caution", "restricted"],
    "open": ["open", "reopened", "restored", "resumed", "cleared", "normal flow"]
}

def extract_with_rules(text: str, title: str = "", corridor: str = "NH-10") -> ExtractedEvent:
    combined = f"{title} {text}".lower()

    # 1. Detect Event Type
    event_type = "other"
    for ev_type, words in EVENT_KEYWORDS.items():
        if any(w in combined for w in words):
            event_type = ev_type
            break

    # 2. Detect Status
    status = "partially_open"
    if any(w in combined for w in STATUS_KEYWORDS["blocked"]):
        status = "blocked"
    elif any(w in combined for w in STATUS_KEYWORDS["open"]):
        status = "open"
    elif any(w in combined for w in STATUS_KEYWORDS["partially_open"]):
        status = "partially_open"

    # If restored event, ensure status is open
    if event_type == "restored":
        status = "open"

    # 3. Detect Road
    road = corridor
    road_match = re.search(r"\b(nh[-\s]?(?:10|6|27|717A|31A))\b", combined, re.IGNORECASE)
    if road_match:
        road = road_match.group(1).upper().replace(" ", "-")

    # 4. Extract Location Text
    location_candidates = [
        "29th Mile", "Teesta Bazar", "Kalijhora", "Sevoke", "Coronation Bridge",
        "Seti Jhora", "Rambi", "Melli", "Rangpo", "Singtam", "Burdang", "Ranipool", "Tadong", "Gangtok",
        "Jorabat", "Byrnihat", "14th Mile", "Nongpoh", "Umsning", "Barapani Bridge", "Umiam Lake",
        "Mawlai", "Shillong", "Police Bazar"
    ]
    location_text = f"{road} Corridor"
    for loc in location_candidates:
        if loc.lower() in combined:
            location_text = loc
            break

    # 5. Extract Severity
    severity = 3
    if status == "blocked" or event_type in ["landslide", "flood"]:
        severity = 5 if "massive" in combined or "submerged" in combined or "washed away" in combined else 4
    elif status == "open" or event_type == "restored":
        severity = 1
    elif status == "partially_open":
        severity = 3

    # 6. Extract Evidence Quote (Under 25 words)
    sentences = re.split(r'[.\n!]', text)
    evidence_quote = ""
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean.split()) >= 4:
            s_lower = s_clean.lower()
            if any(w in s_lower for w in ["landslide", "blocked", "suspended", "waterlogging", "closed", "restored"]):
                evidence_quote = " ".join(s_clean.split()[:22])
                break

    if not evidence_quote:
        evidence_quote = " ".join(text.split()[:20])

    summary = f"{event_type.replace('_', ' ').capitalize()} reported near {location_text} on {road}."
    if status == "blocked":
        summary += " Road completely blocked for traffic."
    elif status == "partially_open":
        summary += " Single-lane / cautious traffic movement advised."
    elif status == "open":
        summary += " Road cleared and restored for regular movement."

    return ExtractedEvent(
        event_type=event_type,
        status=status,
        road=road,
        location_text=location_text,
        severity=severity,
        occurred_at=datetime.now(timezone.utc),
        summary=summary,
        evidence_quote=evidence_quote
    )

def extract_event(text: str, title: str = "", corridor: str = "NH-10") -> ExtractedEvent:
    """
    Step 3: Extract structured incident attributes from raw text.
    Uses rule-based extractor with deterministic accuracy.
    """
    return extract_with_rules(text, title, corridor)
