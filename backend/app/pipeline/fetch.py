from typing import List, Dict, Any
from app.integrations.tinyfish_client import tinyfish
from app.core.logging import logger

def fetch_contents(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Step 2: Fetch rendered contents using TinyFish Fetch API.
    Returns rendered clean text and SHA-256 hashes for provenance and deduplication.
    """
    if not urls:
        return []
    logger.info(f"Invoking TinyFish Fetch for {len(urls)} URLs")
    return tinyfish.fetch(urls)
