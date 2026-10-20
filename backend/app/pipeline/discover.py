from typing import List, Dict, Any
from app.integrations.tinyfish_client import tinyfish
from app.core.logging import logger

DISCOVERY_QUERIES = {
    "NH-10": [
        "NH-10 landslide road blocked Sikkim",
        "Siliguri Gangtok road closure today",
        "Teesta Bazar Kalijhora NH10 traffic advisory",
        "Sikkim 29th mile road condition"
    ],
    "NH-6": [
        "Guwahati Shillong NH6 waterlogging",
        "Jorabat flooded road traffic crawl",
        "Barapani Umiam bridge traffic diversion",
        "Meghalaya Byrnihat NH6 landslip"
    ]
}

def discover_candidates(corridor: str = "NH-10") -> List[Dict[str, Any]]:
    """
    Step 1: Discover candidates using TinyFish Search API.
    Builds corridor-specific search queries, queries TinyFish, drops duplicates and non-relevant items.
    """
    queries = DISCOVERY_QUERIES.get(corridor, DISCOVERY_QUERIES["NH-10"])
    all_results = []
    seen_urls = set()

    for q in queries[:2]:  # Use top 2 queries per run to respect polite rate limits
        logger.info(f"Running TinyFish Discovery for corridor '{corridor}' query: '{q}'")
        results = tinyfish.search(query=q)
        for r in results:
            u = r.get("url")
            if u and u not in seen_urls:
                seen_urls.add(u)
                all_results.append({
                    "title": r.get("title", ""),
                    "url": u,
                    "snippet": r.get("snippet", ""),
                    "query_used": q,
                    "corridor": corridor
                })

    logger.info(f"Discovered {len(all_results)} candidate advisories via TinyFish Search")
    return all_results
