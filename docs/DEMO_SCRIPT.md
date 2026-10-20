# RIDGE Demo Video & Presentation Script (2 to 3 Minutes)

**Title:** RIDGE: Regional Intelligence & Geospatial Efficiency  
**Team:** VISTAARX  
**Hackathon:** KRITICAL HACKS'26 (Track: AI/ML)  

---

### [0:00 - 0:20] The Problem & The Hero Map
- **Screen:** Open Live Map Dashboard on **NH-10 (Siliguri - Gangtok)**.
- **Presenter (VO):**
  > *"Every monsoon, India's North-Eastern Region suffers catastrophic road cut-offs. On vital lifelines like NH-10 connecting Sikkim and NH-6 connecting Meghalaya, sudden landslides and flash floods strand essential freight for days. Existing GPS navigators remain completely blind to these regional advisories.  
  > This is **RIDGE**—an AI-powered logistics intelligence platform that transforms public web advisories into live, risk-aware routing."*
- **Action:** Point out the road segments colored by real-time disruption probability (green, amber, red, and the black blocked section at 29th Mile).

---

### [0:20 - 0:40] Autonomous TinyFish Web Intelligence
- **Screen:** Switch to **TinyFish Pipeline** tab.
- **Presenter (VO):**
  > *"Instead of fragile, bespoke web scrapers that break every week, RIDGE uses **TinyFish** as our sole autonomous web intelligence engine. TinyFish Search monitors regional news, local police Facebook bulletins, and district disaster blogs. TinyFish Fetch renders JavaScript-heavy portals into clean markdown."*
- **Action:**
  1. Click **"Paste Public Advisory URL"** or click **"Discover New Advisories"**.
  2. Paste: `https://sikkimexpress.com/news/nh10-massive-landslide-at-29th-mile-traffic-halted`
  3. Click **"Process URL Live"**.

---

### [0:40 - 1:20] Live Stepper & Provenance
- **Screen:** Watch the real-time visual stepper animate via SSE:  
  `Discover (Search) -> Read (Fetch) -> Extract & Parse -> Gazetteer Geocoding -> Incident Created`.
- **Presenter (VO):**
  > *"Notice the live pipeline stream: TinyFish fetched the page content, extracted structured attributes with Pydantic validation, and our gazetteer snapped the landmark near 29th Mile.  
  > Every incident stores complete cryptographic provenance—source domain, exact quote, fetch timestamp, and an intelligence confidence score. Incidents below 80% confidence are automatically routed to our authority verification queue."*
- **Action:** Click **"Show Reroute on Map"**.

---

### [1:20 - 1:50] Dynamic Risk-Aware Routing
- **Screen:** Route Planner on Live Map.
- **Presenter (VO):**
  > *"Now, when a fleet manager or driver requests a route between Siliguri and Gangtok, our routing engine applies dynamic penalties on the OpenStreetMap graph.  
  > Watch as RIDGE automatically detects the blockage at 29th Mile and calculates the Safest Route via a secondary bypass, cutting disruption exposure by over 75%."*
- **Action:**
  1. Click **"Calculate Safe Route"**.
  2. Highlight the **"Why this route?"** card: *"Rerouted: massive landslide reported near 29th Mile on NH-10. Travel via safe bypass advised."*
  3. Show the direct comparison chart in Insights showing time vs risk trade-off.

---

### [1:50 - 2:15] Authority Verification & Driver In-Cab HUD
- **Screen:** Quick walkthrough of **Verification Queue** and **Fleet & Alerts**.
- **Presenter (VO):**
  > *"For government authorities, the Verification Queue lets disaster officers confirm or reject reports with one click, updating road weights immediately.  
  > Meanwhile, in the cab, drivers receive simplified, high-contrast HUD alerts with actionable instructions before they reach hazardous turns."*
- **Action:** Show the driver tablet HUD view with high-contrast alert.

---

### [2:15 - 2:45] Dashcam-as-a-Service & The Data Flywheel
- **Screen:** **Dashcam DaaS** tab, then **Plans & Pricing**.
- **Presenter (VO):**
  > *"Finally, our sustainable business model: Dashcam-as-a-Service. Commercial trucks in India can't afford ₹50,000 upfront hardware. We supply 4K AI dashcams on a ₹1,499/month subscription.  
  > Dashcams run edge hazard detection, automatically blur license plates and faces with OpenCV, and feed real-time hazard detections back into the public RIDGE map.  
  > That completes our data flywheel: **Smarter logistics. Safer routes. A stronger North-East.**"*
- **Action:** Click **"Simulate Vehicle Hazard Detection"**, then end on the Pricing page.
