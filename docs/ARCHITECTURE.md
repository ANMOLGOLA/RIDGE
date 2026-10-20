# RIDGE System Architecture

```mermaid
graph TD
    PublicWeb["Public Web (Advisories, News, Bulletins)"]
    TinyFish["TinyFish Web Intelligence Layer\n(Search, Fetch, Agent)"]
    Extract["Extraction Pipeline\n(LLM or Rule-based + Gazetteer)"]
    PostGIS[("PostGIS / Database\nIncidents, Segments, Evidence")]
    RiskEngine["Risk Engine (XGBoost)\nWeather + Terrain + Live Incidents"]
    Routing["Risk-Aware Routing Engine\n(OSM Graph + Dynamic Penalties)"]
    FastAPI["FastAPI Backend (REST + SSE)"]
    ReactApp["React 18 + Vite Dashboard\n(Map, Pipeline, Routes, Alerts)"]
    Dashcam["Dashcam DaaS Module\n(Simulated Hazard Stream)"]

    PublicWeb -->|Discover & Read| TinyFish
    TinyFish -->|Clean Text & JSON| Extract
    Extract -->|Dedupe & Confidence| PostGIS
    PostGIS --> RiskEngine
    RiskEngine --> Routing
    Routing --> FastAPI
    PostGIS --> FastAPI
    FastAPI -->|REST + SSE| ReactApp
    Dashcam -->|Hazard Reports| PostGIS
```

## Architectural Highlights
1. **TinyFish Layer**: Zero manual scrapers. TinyFish Search discovers live corridor bulletins, Fetch renders full text, and Agent navigates complex advisory portals.
2. **Confidence Engine**: Multi-factor scoring combining source reputation, corroboration count, geocoding precision, and recency decay. Incidents < 0.50 are routed to the Authority Verification Queue.
3. **ML Risk Engine**: XGBoost classifier trained on corridor features (24h rainfall, slope, river proximity, historical frequency, and live TinyFish alerts) providing 24h disruption probability and SHAP-inspired plain English explanations.
4. **Risk-Aware Routing**: Dynamic cost penalties on the OpenStreetMap graph `cost = travel_time * (1 + alpha * risk) + blocked_penalty`.
5. **Dashcam-as-a-Service**: Hardware-subsidized recurring subscription model streaming vehicle hazard detections back into the public safety network.
