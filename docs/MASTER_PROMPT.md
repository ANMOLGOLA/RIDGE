<USER_REQUEST>
RIDGE MASTER PROMPT: Build the Full Prototype (Frontend to Backend)

How to use this file Paste everything below the line into Claude Code, Cursor, Codex or any coding agent, in an empty repo. Tell it: "Read the whole prompt. Reply with a short plan. Then build phase by phase and commit after each phase." Replace anything in [square brackets] with your own details before pasting.

0. YOUR ROLE

You are a senior full-stack + ML engineer building a working, demo-ready prototype for a hackathon (KRITICAL HACKS'26, track: AI/ML). You write clean, typed, tested, documented code. You work in small phases, commit after each one with a clear message, and never leave the app in a broken state. When a requirement is ambiguous, choose the simplest option that keeps the demo working and note the choice in docs/DECISIONS.md.

1. THE PROJECT IN ONE PARAGRAPH

RIDGE: Regional Intelligence & Geospatial Efficiency. An AI-powered logistics and accessibility intelligence platform for India's North-Eastern Region (NER), where mountainous terrain, heavy rain, landslides and floods regularly block roads. RIDGE continuously collects live road-disruption signals from the open web using TinyFish, converts them into structured, geo-tagged incidents with confidence scores, combines them with weather and terrain features in an ML disruption-risk model, and uses the result to recommend safer routes and send alerts to drivers, fleet managers and authorities. A future business module is Dashcam-as-a-Service: RIDGE-supplied dashcams stream hazard detections that feed the same incident layer (we prototype this as a simulated module).

Tagline: Smarter logistics. Safer routes. A stronger North-East. Team: VISTAARX. Hackathon: KRITICAL HACKS'26.

2. WHAT THE JURY SCORES (build to maximise these)
Criterion	Pts	What you must deliver
Working GitHub project	20	Public repo, working code, clear README, many meaningful commits
TinyFish integration	20	Used meaningfully, functionally and relevantly; explained in README and visible in the demo. A token or decorative use scores poorly
Social media post	10	Provide a ready-to-post draft (section 17)
Technique	10	Clean architecture, typed code, tests, sensible ML pipeline
Innovation and idea	20	Live web intelligence + risk-aware routing + dashcam data flywheel
Impact and usefulness	10	Real problem, realistic scope
Revenue model	10	Pricing page/section consistent with the pitch deck (section 15)

Priority rule: a smooth, working end-to-end demo beats extra features. Never fake the TinyFish step.

3. USERS AND CORE USER STORIES
Fleet manager: sees all vehicles and incidents on a map, gets risk scores for corridors, compares routes, receives alerts.
Driver: asks for the safest route from A to B, gets a simple alert when something changes ahead.
Authority / disaster officer: reviews low-confidence incidents in a verification queue, marks them confirmed or rejected, sees hotspots.
Dashcam fleet customer (business module): sees hazard detections from their vehicles, and an incident evidence log.

Key stories:

As a fleet manager, I paste or let the system find a road advisory and see a new incident appear on the map within seconds, with its source link and confidence.
As a driver, I request a route, and if a segment is blocked or risky the route automatically changes and I see why.
As an officer, I verify or reject uncertain incidents, and this improves future confidence.
As a fleet customer, I upload a dashcam clip or event and a hazard incident is created.
4. TECH STACK (fixed unless a blocker appears)
Frontend: React 18 + Vite + TypeScript, Tailwind CSS, Leaflet (react-leaflet) for maps, TanStack Query for data fetching, Zustand for UI state, Recharts for small charts, Lucide icons.
Backend: Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2 + Alembic, Uvicorn, APScheduler (periodic ingestion), Server-Sent Events (SSE) for live updates.
Database: PostgreSQL + PostGIS (Docker). Redis optional for caching and rate-limit counters (fall back to in-memory if absent).
Geospatial / routing: GeoPandas, Shapely, OSMnx, NetworkX. Use a pre-downloaded, cached road graph (GraphML in data/graphs/) for two demo corridors so nothing depends on live OSM downloads during the demo.
ML: scikit-learn, XGBoost, pandas, numpy, joblib, SHAP (or XGBoost feature importance fallback).
Web intelligence: TinyFish (official Python SDK pip install tinyfish).
LLM extraction (pluggable): LLM_PROVIDER=anthropic|none. If none or no key, use the rule-based extractor (regex + gazetteer). The app must work in both modes.
Weather: Open-Meteo forecast API (free, no key) for rainfall features, with cached fixtures as fallback.
Alerts: in-app alert feed (SSE) is required. Twilio SMS/WhatsApp is an optional stub behind a feature flag.
DevOps: Docker Compose (db, backend, frontend), .env.example, Makefile, GitHub Actions (lint + tests).
5. DEMO CORRIDORS AND SEED DATA

Use two bounded corridors so the graph is small and fast:

NH-10: Siliguri to Gangtok (West Bengal / Sikkim), landslide-prone.
NH-6 / NH-27 region: Guwahati to Shillong (Assam / Meghalaya), flood and rain-prone.

Seed data/gazetteer.json with ~60 named places, towns, bridges and landmarks per corridor (name, lat, lon, aliases), used for geocoding extracted place names. Seed data/fixtures/ with:

12 realistic sample advisory texts (closures, landslides, waterlogging, bridge damage, restored roads) saved as .json with url, title, text, published_at. Label them clearly as fixtures for offline testing only.
cached weather responses and a few cached TinyFish responses so the app can run offline in "fixture mode".
6. ARCHITECTURE
Public web (advisories, news, bulletins)
        |
   TinyFish layer  --- Search -> Fetch -> (Agent / Browser for hard portals)
        |
   Extraction (LLM or rules) -> Geocoder (gazetteer + OSM) -> Dedupe + Confidence
        |
   PostGIS: incidents, segments, observations
        |
   Risk engine (XGBoost + rules)  <-- weather + terrain + history + incidents
        |
   Routing engine (NetworkX on OSM graph, risk-weighted)
        |
   FastAPI  -- REST + SSE -->  React dashboard (map, routes, alerts, verification)
        ^
   Dashcam module (simulated hazard events) feeds incidents too
Repository layout
ridge/
  README.md
  docker-compose.yml
  .env.example
  Makefile
  docs/ (ARCHITECTURE.md, DECISIONS.md, TINYFISH.md, API.md, DEMO_SCRIPT.md, screenshots/)
  data/ (gazetteer.json, fixtures/, graphs/, models/)
  backend/
    app/
      main.py, config.py, deps.py
      api/ (incidents.py, routes.py, risk.py, alerts.py, ingestion.py, dashcam.py, fleet.py, health.py)
      core/ (db.py, models.py, schemas.py, events.py, logging.py)
      integrations/
        tinyfish_client.py      # ONLY place that talks to TinyFish
        weather.py
        llm.py
      pipeline/
        discover.py   # TinyFish Search
        fetch.py      # TinyFish Fetch
        extract.py    # LLM or rule-based extraction
        geocode.py
        dedupe.py
        confidence.py
        runner.py     # orchestrates a full ingestion run + emits step events
      ml/
        features.py, synth_data.py, train.py, predict.py, explain.py
      routing/ (graph.py, weights.py, planner.py)
      dashcam/ (detector.py, privacy.py, simulator.py)
    tests/
    pyproject.toml
  frontend/
    src/ (pages/, components/, hooks/, lib/, store/, styles/)
    package.json, vite.config.ts, tailwind.config.ts
7. TINYFISH INTEGRATION (MANDATORY AND MEANINGFUL)

Before coding this part: fetch https://docs.tinyfish.ai/llms.txt and the "For Coding Agents" page, and follow the official docs. Do not invent endpoints.

Facts to rely on (verify against docs):

Auth: header X-API-Key, env var TINYFISH_API_KEY.
Search API: GET https://api.search.tinyfish.ai?query=... returns ranked results (title, snippet, url). Python: client.search.query(query="..."). Free. Free tier is limited (about 5 queries per minute), so cache and throttle.
Fetch API: POST https://api.fetch.tinyfish.ai renders pages (including JavaScript-heavy ones) and returns clean content. Python: client.fetch.get_contents(urls=[...]). Free. Limited to roughly 25 URLs per minute.
Agent API: https://agent.tinyfish.ai/v1/automation/... with /run, /run-async, /run-sse. Takes a natural-language goal and operates a real site. Uses credits (the hackathon gives $13), so use it sparingly.
Browser API: POST https://api.browser.tinyfish.ai creates a remote browser for Playwright/CDP. Uses credits. Optional.
How RIDGE uses TinyFish (all four stages must be real)
Discover (Search): every ingestion run builds queries from the corridor and event types, for example NH-10 landslide road blocked Sikkim, Siliguri Gangtok road closure today, Guwahati Shillong NH6 waterlogging, Assam flood road damage bridge. Call Search, keep the top results, drop duplicates and non-relevant domains.
Read (Fetch): pass the result URLs to Fetch to get clean text. Store raw content, the URL, fetch time and a content hash (for provenance and dedupe).
Act (Agent, hard cases): for one configured portal-style source (a public advisory/bulletin page that needs navigation), run an Agent goal such as: "Open this page, find the latest road closure or traffic advisory entries, and return them as a JSON list with fields road, location, status, date." Cache the result and provide a fixture. Gate it behind ENABLE_TINYFISH_AGENT=true.
Handle hard pages (Browser, optional): wrapper exists but is off by default.
Requirements for the integration code
All TinyFish calls live in integrations/tinyfish_client.py with typed methods: search(query), fetch(urls), run_agent(goal, url).
Rate limiting, retries with backoff, timeouts, and a disk cache keyed by request hash.
TINYFISH_MODE=live|fixture. In fixture mode, return cached responses so the app is testable offline. The live path must be the default for the demo.
Every incident stores provenance: source URL, domain, fetched_at, snippet used, which TinyFish API produced it.
A GET /api/ingestion/runs/{id} endpoint and an SSE stream /api/stream/pipeline expose each step (search_started, results_found, fetch_done, extracted, geocoded, incident_created) so the frontend can visualise the TinyFish pipeline live.
Respect site terms and robots rules: only public pages, polite rates, no login-gated or personal data.
docs/TINYFISH.md must explain exactly where and why each TinyFish API is used, with a sequence diagram (Mermaid), sample request/response, and a screenshot reference.
8. EXTRACTION, GEOCODING, DEDUPE, CONFIDENCE

Extraction output schema (Pydantic):

ExtractedEvent {
  event_type: landslide | flood | waterlogging | road_closed | bridge_damage | accident | restored | other
  status: blocked | partially_open | open | unknown
  road: str | null            # e.g. "NH-10"
  location_text: str          # e.g. "near Teesta Bazar"
  severity: 1-5
  occurred_at: datetime | null
  summary: str                # one sentence
  evidence_quote: str         # short snippet, under 25 words
}
LLM mode: prompt the model to return JSON only, validate with Pydantic, retry once on invalid JSON. Reject anything the page does not support.
Rule mode: keyword lists (landslide, washed away, blocked, waterlogged, restored, one-way) + regex for road codes (NH[-\s]?\d+[A-Z]?) + gazetteer matching.
Geocoding: match location_text against gazetteer aliases (fuzzy match with rapidfuzz), snap the point to the nearest road-graph edge within 500 m. If no match, keep the incident as unlocated and exclude it from routing.
Dedupe: same road + event type + within 2 km + within 6 hours merges into one incident and increases source_count.
Confidence (0 to 1): weighted score from source count, source reliability tier (official domain > established news > other), recency decay, extraction validity, geocoding precision. Store the breakdown. Incidents below 0.5 go to the verification queue.
Lifecycle: active, monitoring, resolved (auto-resolve on a "restored" signal or after N hours with no new evidence).
9. RISK ENGINE (ML)

Goal: predict disruption risk (0 to 1) per road segment for the next 24 hours, with an explanation.

Features per segment: rainfall last 24h and forecast next 24h (Open-Meteo), terrain slope class, landslide-susceptibility zone flag (from a bundled GeoJSON stub, documented as approximate), distance to rivers/bridges, road class, historical incident count nearby, live incidents within 5 km (from TinyFish), hour/season.

Training data: real labelled NER data is not available in the hackathon window, so generate a documented synthetic dataset in ml/synth_data.py using domain rules plus noise, then train XGBoost. In the README and UI footer, state clearly: "Model trained on synthetic data for the prototype. Replace with historical incident data for production." Do not hide this. If time allows, add a small hand-labelled real sample from fixtures.

Pipeline: train.py produces data/models/risk_xgb.joblib and a metrics JSON (AUC, precision/recall, confusion matrix). predict.py scores all segments and caches results. explain.py returns the top 3 contributing factors per segment in plain English (for example "Heavy rain forecast + landslide zone + 2 live reports nearby").

Final label: risk < 0.35 open, 0.35 to 0.65 risky, > 0.65 high risk. Any segment within 300 m of an active confirmed blocked incident is forced to blocked.

10. ROUTING ENGINE
Load the cached OSM graph (drive network) for each corridor.
Edge cost = travel_time * (1 + alpha * risk) + blocked_penalty. alpha default 3, configurable. Blocked edges are removed unless no path exists (then return the least-bad path with a warning).
POST /api/routes returns up to 3 alternatives (fastest, safest, balanced) with distance, ETA, mean and max risk, list of risky segments, and a plain-English reason ("Rerouted: landslide reported near Teesta Bazar 38 minutes ago").
Return GeoJSON LineStrings for the map.
Provide GET /api/routes/compare data: baseline route vs RIDGE route for the same OD pair (used in the demo and a small chart).
11. BACKEND API (REST + SSE)

All responses typed with Pydantic. Prefix /api. Document in OpenAPI and docs/API.md.

GET /health - status, TinyFish mode, model loaded, DB ok
GET /incidents?status=&min_confidence=&corridor= - list (GeoJSON option)
GET /incidents/{id} - details with provenance and confidence breakdown
POST /incidents/{id}/verify - body {decision: "confirm"|"reject", note}; updates status and confidence; logs the verifier
POST /ingestion/run - body {corridor, mode: "search"|"url", url?}; starts a run, returns run_id. mode=url lets the demo paste a single advisory URL.
GET /ingestion/runs/{id} - steps and results
GET /stream/pipeline - SSE of pipeline step events
GET /stream/alerts - SSE of new alerts
GET /risk/segments?corridor= - GeoJSON with risk, label, explanation
POST /routes - body {origin, destination, preference} (coordinates or place names)
GET /routes/compare
GET /alerts, POST /alerts/subscribe (vehicle or phone number, optional)
GET /fleet/vehicles, POST /fleet/vehicles/{id}/position (simulated GPS ticks)
POST /dashcam/events and POST /dashcam/upload (section 13)
GET /metrics/summary - counts, average confidence, hotspots, model metrics

Background jobs: APScheduler runs ingestion every INGEST_INTERVAL_MIN (default 15) and a risk refresh every 30 minutes. Both can be triggered manually from the UI.

Database tables (PostGIS): sources, raw_documents, incidents (geometry Point, status, confidence, breakdown JSON, provenance JSON), incident_evidence, verifications, road_segments (edge id, geometry LineString, attributes), risk_scores, vehicles, vehicle_positions, alerts, ingestion_runs, ingestion_steps, dashcam_events. Add spatial indexes. Provide Alembic migrations and make seed.

12. FRONTEND (WHAT TO BUILD, SCREEN BY SCREEN)

Design system: match the pitch deck. Navy 
#002060, orange 
#FF5C1F, deep navy 
#0B1B3F, light card 
#F3F6FC, border 
#D3DDF2, text 
#1F2A44. Rounded cards, soft shadows, clear hierarchy. Light and dark mode. Fully responsive (desktop first, usable on mobile). Accessible: keyboard navigation, colour-blind-safe risk palette plus icons, ARIA labels. Include a footer note about synthetic-model data.

Global layout: top bar (logo "RIDGE", corridor switcher, TinyFish status pill showing Live/Fixture, last ingestion time, "Run ingestion" button), left nav, main content.

Page 1: Live Map Dashboard (the hero screen)
Full-height Leaflet map. Road segments coloured by risk (green, amber, red, black for blocked) from /risk/segments.
Incident markers with icons per type. Popup/side panel shows summary, severity, confidence meter, source link, fetched time, evidence quote, "Verified by" status.
Route planner panel: origin and destination inputs (autocomplete from gazetteer or click on map), preference toggle (Fastest / Safest / Balanced). Draw alternatives in different colours with ETA, distance, mean/max risk. A "Why this route?" card with the plain-English reason.
Live alert feed (right rail) via SSE with toast notifications.
Layer toggles: risk, incidents, vehicles, dashcam hazards.
KPI strip: active incidents, average confidence, blocked segments, routes rerouted today.
Page 2: TinyFish Live Pipeline (the demo-winner screen)
A visual stepper: Search -> Fetch -> Extract -> Geocode -> Incident created, animated from the SSE stream.
Show real data per step: the queries sent, number of results, URLs fetched, extracted JSON, geocoded point.
A prominent "Paste advisory URL" box that triggers mode=url. On success, link to the new incident on the map and offer a "Show reroute" button that opens the route planner pre-filled with an affected route.
A table of recent ingestion runs with status, duration, counts, and which TinyFish API was used.
Always show a small "Powered by TinyFish" mark with a link to the docs.
Page 3: Verification Queue (authority view)
List of incidents below the confidence threshold. Side-by-side: extracted data and source snippet/link. Confirm / Reject / Add note. Confidence updates immediately and the map reflects it.
Page 4: Fleet and Alerts
Vehicle list with simulated positions moving along routes. When a route becomes risky, show an alert to the affected vehicle and a suggested reroute. A small "Driver view" panel with big, simple text for the alert.
Page 5: Dashcam Module (business module, prototype level)
Cards: devices, recent detections, evidence log. Upload a short clip or image, or press "Simulate detections". Show detected hazard type, location, confidence, privacy-blurred preview, and a button "Create incident". Clearly label simulated data as "Simulation".
A "Benefits for your fleet" panel summarising: hazard alerts, evidence for insurance, driver coaching metrics, ETA accuracy (mock numbers, labelled demo).
Page 6: Insights
Charts: incidents over time, hotspots by road, confidence distribution, baseline vs RIDGE route comparison, model metrics and feature importance.
Page 7: Plans and Pricing (revenue model, matches the deck)
Starter Rs 999, Pro Rs 1,499 (highlighted), Enterprise custom, all "per vehicle per month, hardware included". A short "Why these prices" box (below Dacio.ai's Rs 2,000 lease; 36-month Pro total Rs 53,964 vs Rs 35,000-75,000 up-front dashcams). A small unit-economics card marked "team estimates, to be validated in a pilot" (hardware Rs 8,000, cloud Rs 300/month, payback about 7 months).

Frontend quality rules: loading, empty and error states everywhere; skeletons; no layout jumps; typed API client generated from OpenAPI or hand-typed in lib/api.ts; environment-based API URL; unit tests for utilities and 2 to 3 component tests.

13. DASHCAM MODULE (SIMULATED, CLEARLY LABELLED)
dashcam/simulator.py: emits plausible hazard events (pothole, debris, waterlogging, landslide material) along the demo corridors with confidence values.
dashcam/detector.py: optional lightweight detector (for example a small pretrained YOLO model via ultralytics, behind ENABLE_VISION=true). If disabled or unavailable, the upload endpoint returns a clearly flagged simulated detection. Never present simulated output as real detection.
dashcam/privacy.py: OpenCV-based face and number-plate blur demo on uploaded images (Haar cascade is acceptable for the prototype). Document limitations.
Dashcam events become incidents with source=dashcam, feed the confidence calculation (a dashcam report plus a web report increases confidence), and appear on the map.
14. ALERTS
Rule: when a new or upgraded incident intersects a vehicle's active route or the corridor a user follows, create an alert with message, severity, suggested action and link to the reroute.
Delivery: SSE in-app (required). Optional Twilio WhatsApp/SMS behind ENABLE_TWILIO=true with environment credentials, never committed.
De-duplicate alerts, and cap frequency per vehicle.
15. BUSINESS AND REVENUE CONTENT (KEEP CONSISTENT WITH THE DECK)
Model: Dashcam-as-a-Service. RIDGE supplies the dashcam, the logistics company subscribes.
Benchmarks (public figures): Dacio.ai leases AI dashcams at about Rs 2,000 per vehicle per month; buying an AI dashcam outright costs roughly Rs 12,000-75,000; India's fleet-management market is projected at $4.79B by FY32 (15.25% CAGR); over 75% of commercial vehicles are owned by small and mid-sized operators.
Streams: fleet subscriptions (core), risk-data API (phase 2), government dashboards (phase 2).
Put these in the Plans page and in the README's "Business model" section with sources.
16. QUALITY BAR AND CONSTRAINTS
Honesty: label synthetic data, simulated dashcam output, and fixture mode wherever they appear. No fake "AI" claims.
Secrets: never commit keys. Provide .env.example with TINYFISH_API_KEY, TINYFISH_MODE, ENABLE_TINYFISH_AGENT, LLM_PROVIDER, ANTHROPIC_API_KEY, DATABASE_URL, REDIS_URL, INGEST_INTERVAL_MIN, ENABLE_VISION, ENABLE_TWILIO.
Resilience: if TinyFish, weather or the LLM fails, degrade gracefully with clear UI messages, never crash.
Performance: map loads in under 3 seconds with the cached graph; route requests under 1.5 seconds; ingestion runs asynchronously.
Security: validate all input, CORS configured, rate-limit public endpoints, no PII storage, parameterised queries only.
Testing: pytest for extraction (rule mode), geocoding, dedupe, confidence, routing weights and API smoke tests; fixtures make tests deterministic. Frontend: Vitest basics. CI runs lint and tests.
Code style: ruff + black + mypy (backend), ESLint + Prettier + strict TypeScript (frontend).
Run experience: docker compose up starts everything. make seed loads data and trains the model. make demo runs a scripted demo ingestion. The app must run on a fresh machine within about 10 minutes.
17. README, DOCS AND SOCIAL POST (SCORED, DO NOT SKIP)

README.md must contain, in this order:

Title, tagline, badges, a hero screenshot/GIF placeholder docs/screenshots/hero.gif
The problem and why the North-East
What RIDGE does (feature list)
How TinyFish is used (short, with the pipeline diagram and link to docs/TINYFISH.md)
Architecture diagram (Mermaid)
Tech stack
Quick start (Docker and manual), environment variables, how to get the TinyFish key
Demo walkthrough (the 2 to 3 minute script) and links: [demo video], [social post]
ML model: features, training data (synthetic, stated honestly), metrics
Business model and pricing with sources
Roadmap / future scope (dashcam rollout, offline-first edge mode, IoT sensors, open risk API, planning tools for authorities)
Limitations and ethics (synthetic data, privacy, source reliability)
Team VISTAARX, licence

docs/DEMO_SCRIPT.md (2 to 3 minutes):

0:00 Problem in one sentence over the map showing risky roads.
0:20 Open the TinyFish pipeline page, paste a real advisory URL.
0:40 Watch Search, Fetch, Extract, Geocode happen live; show the incident, source link and confidence.
1:20 Open the route planner on an affected route; show baseline vs RIDGE reroute and the reason.
1:50 Show the verification queue and the fleet alert.
2:15 Show the dashcam module and the pricing page; close on the data flywheel.

Social post draft (generate in docs/SOCIAL_POST.md): 120 to 160 words, plain language, what it does, who it helps, what makes it cool, GitHub link placeholder, demo video or GIF placeholder, 3 to 5 hashtags. It does not need to mention the hackathon.

18. BUILD PLAN (WORK IN THIS ORDER, COMMIT AFTER EACH PHASE)

Phase 0: Scaffold (about 30 min). Repo, Docker Compose, FastAPI hello, Vite app, CI, .env.example, health endpoint, base layout and theme. Done when: docker compose up shows the frontend talking to /health.

Phase 1: Data and map (about 1 h). PostGIS schema, migrations, gazetteer, cached road graphs, segments endpoint, Leaflet map with segments and static seed incidents. Done when: the map renders both corridors with coloured segments.

Phase 2: TinyFish pipeline (the core, about 2 h). tinyfish_client.py, discover, fetch, extract (rules first, LLM optional), geocode, dedupe, confidence, runner, SSE events, ingestion endpoints, TinyFish pipeline page, paste-URL flow. Done when: pasting a real URL creates an incident with provenance on the map, live. Test with the real API key before moving on.

Phase 3: Risk engine (about 1.5 h). Synthetic data, features, XGBoost training, predictions, explanations, risk-coloured map, insights metrics.

Phase 4: Routing (about 1.5 h). Weighted planner, alternatives, reasons, comparison chart, route panel UI. Done when: a new incident visibly changes the suggested route.

Phase 5: Alerts, verification and fleet (about 1.5 h). Alert rules and SSE feed, verification queue, simulated vehicles.

Phase 6: Dashcam and plans (about 1.5 h). Simulator, upload with privacy blur, incident creation, benefits panel, pricing page.

Phase 7: Polish and submission (about 1.5 h). Empty/error states, responsive pass, README, docs, screenshots, demo script, social post draft, record-ready demo data (make demo), final test run.

If time is short, protect this minimum: Phases 0, 1, 2, 4 and the README. These alone deliver TinyFish integration, a working map, rerouting and a clear story.

19. WHAT TO DO FIRST
Read this whole prompt. Fetch the TinyFish docs index (https://docs.tinyfish.ai/llms.txt).
Reply with a concise plan: assumptions, risks, any questions that truly block progress (maximum 3).
Then start Phase 0. After each phase: run tests, run the app, summarise what works, list known gaps, and commit with a message like feat(pipeline): TinyFish search and fetch with caching.
At the end, produce a final checklist against section 2 and section 17, stating honestly what is complete, simulated, or missing.

Begin now.
</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-10-20T17:14:45+05:30.
</ADDITIONAL_METADATA>
<USER_SETTINGS_CHANGE>
The user changed setting `Model Selection` from None to Gemini 3.8 Flash (High). No need to comment on this change if the user doesn't ask about it. If reporting what model you are, please use a human readable name instead of the exact string.
</USER_SETTINGS_CHANGE>