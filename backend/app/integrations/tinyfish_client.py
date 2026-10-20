import os
import json
import hashlib
import time
import httpx
from typing import List, Dict, Any, Optional
from app.config import settings
from app.core.logging import logger

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "cache", "tinyfish")
FIXTURES_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "fixtures", "tinyfish_responses.json")

class TinyFishClient:
    """
    Official TinyFish Web Intelligence client for RIDGE.
    Supports Search API, Fetch API, and Agent API with disk caching, rate limiting, and fixture mode.
    """
    def __init__(self):
        self.api_key = settings.TINYFISH_API_KEY
        self.mode = settings.TINYFISH_MODE.lower()  # "live" | "fixture"
        self.search_url = "https://api.search.tinyfish.ai"
        self.fetch_url = "https://api.fetch.tinyfish.ai"
        self.agent_url = "https://agent.tinyfish.ai/v1/automation/run"
        os.makedirs(CACHE_DIR, exist_ok=True)
        self._load_fixtures()

    def _load_fixtures(self):
        self.fixtures = {"search": {}, "fetch": {}}
        if os.path.exists(FIXTURES_FILE):
            try:
                with open(FIXTURES_FILE, "r", encoding="utf-8") as f:
                    self.fixtures = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load TinyFish fixtures: {e}")

    def _cache_key(self, prefix: str, data: Any) -> str:
        serialized = json.dumps(data, sort_keys=True)
        h = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return os.path.join(CACHE_DIR, f"{prefix}_{h}.json")

    def _read_cache(self, prefix: str, data: Any) -> Optional[Any]:
        key_file = self._cache_key(prefix, data)
        if os.path.exists(key_file):
            try:
                with open(key_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def _write_cache(self, prefix: str, data: Any, result: Any):
        key_file = self._cache_key(prefix, data)
        try:
            with open(key_file, "w", encoding="utf-8") as f:
                json.dump(result, f)
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")

    def search(self, query: str, location: str = "IN", language: str = "en") -> List[Dict[str, Any]]:
        """
        Discovers fresh advisories, bulletins, and local news across dynamic keywords.
        Returns list of {title, url, snippet}.
        """
        # 1. Check disk cache
        cache_data = {"query": query, "location": location, "language": language}
        cached = self._read_cache("search", cache_data)
        if cached is not None:
            logger.info(f"TinyFish Search Cache Hit for: '{query}'")
            return cached

        # 2. Check fixture mode or missing API key
        if self.mode == "fixture" or not self.api_key:
            logger.info(f"TinyFish Search running in FIXTURE mode for: '{query}'")
            # Match query in fixtures or return default
            for k, results in self.fixtures.get("search", {}).items():
                if any(word in query.lower() for word in ["nh-10", "sikkim"]) and "nh-10" in k.lower():
                    return results
                if any(word in query.lower() for word in ["nh-6", "shillong", "guwahati"]) and "nh6" in k.lower():
                    return results
            # Fallback to any search fixture
            first_key = next(iter(self.fixtures.get("search", {})), None)
            return self.fixtures.get("search", {}).get(first_key, [])

        # 3. Live API call
        headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json"
        }
        params = {
            "query": query,
            "location": location,
            "language": language
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(self.search_url, headers=headers, params=params)
                if res.status_code == 200:
                    data = res.json()
                    results = data.get("results", [])
                    self._write_cache("search", cache_data, results)
                    return results
                else:
                    logger.error(f"TinyFish Search error [{res.status_code}]: {res.text}")
                    # Degrade gracefully to fixture
                    return self.fixtures.get("search", {}).get("NH-10 landslide road blocked Sikkim", [])
        except Exception as e:
            logger.error(f"TinyFish Search request exception: {e}")
            return self.fixtures.get("search", {}).get("NH-10 landslide road blocked Sikkim", [])

    def fetch(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Cleanly renders JS and regional news portals, returning markdown/clean text and hashes.
        Returns list of {url, status, content, content_hash}.
        """
        if not urls:
            return []

        # 1. Check disk cache
        cache_data = {"urls": sorted(urls)}
        cached = self._read_cache("fetch", cache_data)
        if cached is not None:
            logger.info(f"TinyFish Fetch Cache Hit for {len(urls)} URLs")
            return cached

        # 2. Fixture mode or missing API key
        if self.mode == "fixture" or not self.api_key:
            logger.info(f"TinyFish Fetch running in FIXTURE mode for {len(urls)} URLs")
            res_list = []
            for u in urls:
                if u in self.fixtures.get("fetch", {}):
                    item = self.fixtures["fetch"][u]
                    res_list.append({
                        "url": u,
                        "status": item.get("status", 200),
                        "content": item.get("content", ""),
                        "content_hash": hashlib.sha256(item.get("content", "").encode("utf-8")).hexdigest()
                    })
                else:
                    # Generic simulated clean text for unlisted URL
                    sample_content = f"# Road Disruption Bulletin\n\nAdvisory reported from {u}. Traffic movement disrupted due to landslide and fallen debris."
                    res_list.append({
                        "url": u,
                        "status": 200,
                        "content": sample_content,
                        "content_hash": hashlib.sha256(sample_content.encode("utf-8")).hexdigest()
                    })
            return res_list

        # 3. Live API call
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {"urls": urls}
        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(self.fetch_url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    results = []
                    for item in data.get("results", []):
                        cnt = item.get("content", "")
                        results.append({
                            "url": item.get("url"),
                            "status": item.get("status", 200),
                            "content": cnt,
                            "content_hash": hashlib.sha256(cnt.encode("utf-8")).hexdigest()
                        })
                    self._write_cache("fetch", cache_data, results)
                    return results
                else:
                    logger.error(f"TinyFish Fetch error [{res.status_code}]: {res.text}")
                    return []
        except Exception as e:
            logger.error(f"TinyFish Fetch exception: {e}")
            return []

    def run_agent(self, goal: str, url: str) -> Optional[Dict[str, Any]]:
        """
        TinyFish Agent API for navigating multi-step advisory portals.
        Gated behind ENABLE_TINYFISH_AGENT=true.
        """
        if not settings.ENABLE_TINYFISH_AGENT:
            logger.info("TinyFish Agent is disabled via configuration.")
            return None

        if self.mode == "fixture" or not self.api_key:
            return {
                "status": "success",
                "goal": goal,
                "url": url,
                "bulletins": [
                    {"road": "NH-10", "location": "29th Mile", "status": "blocked", "date": "Today"}
                ]
            }

        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {"goal": goal, "url": url}
        try:
            with httpx.Client(timeout=60.0) as client:
                res = client.post(self.agent_url, headers=headers, json=payload)
                if res.status_code == 200:
                    return res.json()
                else:
                    logger.error(f"TinyFish Agent error [{res.status_code}]: {res.text}")
                    return None
        except Exception as e:
            logger.error(f"TinyFish Agent exception: {e}")
            return None

tinyfish = TinyFishClient()
