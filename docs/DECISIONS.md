# RIDGE Architecture & Implementation Decisions

### 1. Zero-Setup Local Development with SQLite & PostGIS Dual-Mode
- **Context:** To ensure seamless evaluation without requiring Docker or a running PostgreSQL/PostGIS server on developer machines, the database layer supports standard SQLite with GeoJSON geometries alongside PostgreSQL/PostGIS.
- **Decision:** Use SQLAlchemy with flexible spatial columns (GeoJSON text or WKT in SQLite, Geometry types in PostGIS). Docker Compose spins up real PostGIS 16.

### 2. TinyFish Official SDK & Direct REST Fallback
- **Context:** TinyFish provides an official Python SDK (`tinyfish`) and REST endpoints (`api.search.tinyfish.ai`, `api.fetch.tinyfish.ai`, `agent.tinyfish.ai`).
- **Decision:** Implement `TinyFishClient` in `backend/app/integrations/tinyfish_client.py` wrapping the SDK with automatic local caching, rate limiting, and an explicit `fixture` mode so tests and offline demos never break or exceed API quotas.

### 3. Synthetic Risk Model Grounding
- **Context:** Real labelled disruption datasets for the North-Eastern Region over granular road segments are unavailable within the hackathon timeframe.
- **Decision:** As explicitly specified, synthesize realistic data in `ml/synth_data.py` grounded in real geomorphology and weather features (slope, rainfall, proximity to rivers, history) and train XGBoost. Transparently label synthetic components in the UI and README.

### 4. Bounded Demo Corridors
- **Context:** Downloading and routing full OpenStreetMap networks for India is slow and bandwidth-intensive.
- **Decision:** Pre-bundle high-resolution road network graphs (`GraphML`) for the two specified corridors:
  1. **NH-10:** Siliguri to Gangtok (West Bengal / Sikkim)
  2. **NH-6 / NH-27:** Guwahati to Shillong (Assam / Meghalaya)
  Both corridors are backed by ~60 gazetteer landmarks each for instant fuzzy geocoding and routing without external network dependencies.
