# RIDGE REST & SSE API Reference

All REST endpoints are prefixed with `/api`. Documentation is also interactively available at `/docs` (Swagger UI) and `/redoc`.

---

## 1. Health & Status
- **`GET /api/health`**
  - **Description**: Returns operational status, configured TinyFish mode (`live` | `fixture`), ML model loading state, and database connectivity.
  - **Response 200**:
    ```json
    {
      "status": "healthy",
      "service": "RIDGE Regional Intelligence API",
      "version": "0.1.0",
      "tinyfish_mode": "fixture",
      "tinyfish_configured": false,
      "tinyfish_agent_enabled": false,
      "llm_provider": "none",
      "db_ok": true,
      "model_loaded": true,
      "corridors": ["NH-10 (Siliguri - Gangtok)", "NH-6/27 (Guwahati - Shillong)"]
    }
    ```

---

## 2. Risk Engine
- **`GET /api/risk/segments?corridor={NH-10|NH-6}`**
  - **Description**: Returns road segments with their real-time or XGBoost-predicted disruption probability as a GeoJSON FeatureCollection.
  - **Response 200**:
    ```json
    {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": {
            "type": "LineString",
            "coordinates": [[88.4312, 26.7271], [88.4011, 26.7642]]
          },
          "properties": {
            "id": "seg_nh10_001",
            "corridor": "NH-10",
            "name": "Siliguri Junction to Mahananda Wildlife Sanctuary Gate",
            "risk_score": 0.12,
            "risk_label": "open",
            "explanation": "Normal baseline conditions"
          }
        }
      ]
    }
    ```

---

## 3. Incidents & Provenance
- **`GET /api/incidents?corridor={corridor}&status={status}&min_confidence={conf}`**
  - **Description**: Lists active road disruption incidents with provenance, source links, and confidence metrics.
- **`GET /api/incidents/{id}`**
  - **Description**: Detailed record of an incident including exact evidence quote, geocoding precision, and verification history.
- **`POST /api/incidents/{id}/verify`**
  - **Description**: Official confirmation or rejection by an authority officer. Immediately updates confidence score and segment blockage state.
  - **Request Body**:
    ```json
    {
      "decision": "confirm",
      "note": "Verified by Kalimpong disaster duty officer",
      "verifier": "State Disaster Management Officer"
    }
    ```

---

## 4. TinyFish Ingestion Pipeline
- **`POST /api/ingestion/run`**
  - **Description**: Triggers a live or URL-based TinyFish web intelligence crawl.
  - **Request Body**:
    ```json
    {
      "corridor": "NH-10",
      "mode": "search"
    }
    ```
    Or paste URL mode:
    ```json
    {
      "corridor": "NH-10",
      "mode": "url",
      "url": "https://sikkimexpress.com/news/nh10-massive-landslide-at-29th-mile-traffic-halted"
    }
    ```
- **`GET /api/ingestion/runs`**
  - **Description**: Returns history of recent runs, duration, and TinyFish APIs invoked.
- **`GET /api/stream/pipeline`**
  - **Description**: SSE stream broadcasting pipeline execution steps:
    `search_started` -> `results_found` -> `fetch_done` -> `extracted` -> `geocoded` -> `incident_created`.

---

## 5. Risk-Aware Routing
- **`POST /api/routes`**
  - **Description**: Computes up to 3 alternative paths (Safest, Balanced, Fastest) on the corridor road graph with dynamic risk penalties.
  - **Request Body**:
    ```json
    {
      "origin": "Siliguri Junction",
      "destination": "Gangtok MG Marg",
      "preference": "safest",
      "corridor": "NH-10"
    }
    ```
- **`GET /api/routes/compare?corridor={corridor}&origin={origin}&destination={destination}`**
  - **Description**: Returns comparative transit metrics and risk reduction percentage between the baseline direct route and the RIDGE safest route.

---

## 6. Dashcam Telemetry & Hardware DaaS
- **`GET /api/dashcam/events`**: Lists recent vehicle edge detections.
- **`POST /api/dashcam/simulate`**: Simulates forward-facing AI camera hazard detection.
- **`POST /api/dashcam/upload`**: Accepts image/video upload and applies OpenCV privacy blur on license plates and faces before logging hazard.
