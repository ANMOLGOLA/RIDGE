from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
import json
import os

router = APIRouter(prefix="/gazetteer", tags=["Gazetteer"])

GAZETTEER_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "gazetteer.json")

def load_gazetteer_data():
    if os.path.exists(GAZETTEER_PATH):
        with open(GAZETTEER_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@router.get("", response_model=List[Dict[str, Any]])
def get_gazetteer(
    corridor: Optional[str] = Query(None, description="Filter by corridor e.g. NH-10 or NH-6"),
    query: Optional[str] = Query(None, description="Fuzzy match landmark name or alias")
):
    items = load_gazetteer_data()
    if corridor:
        items = [i for i in items if i.get("corridor") == corridor]
    if query:
        q = query.lower()
        items = [
            i for i in items
            if q in i.get("name", "").lower() or any(q in a.lower() for a in i.get("aliases", []))
        ]
    return items
