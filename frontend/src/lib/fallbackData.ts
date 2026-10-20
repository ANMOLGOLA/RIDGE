import type { GeoJSONFeatureCollection, Incident, AlertItem, MetricsSummary } from './api';

export const FALLBACK_SEGMENTS_NH10: GeoJSONFeatureCollection = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      geometry: {
        type: "LineString",
        coordinates: [[88.4312, 26.7271], [88.4011, 26.7642], [88.3615, 26.7905]]
      },
      properties: {
        id: "seg_nh10_001",
        edge_id: "nh10_e_001",
        corridor: "NH-10",
        road_name: "NH-10",
        name: "Siliguri Junction to Sukna Checkpost",
        start_node: "Siliguri Junction",
        end_node: "Sukna Checkpost",
        start_lat: 26.7271,
        start_lon: 88.4312,
        end_lat: 26.7905,
        end_lon: 88.3615,
        length_m: 8500,
        base_travel_time_sec: 600,
        slope_deg: 2.5,
        river_proximity_m: 450,
        landslide_zone: false,
        historical_incident_count: 1,
        risk_score: 0.12,
        risk_label: "open",
        explanation: "Normal baseline traffic flow"
      }
    },
    {
      type: "Feature",
      geometry: {
        type: "LineString",
        coordinates: [[88.3615, 26.7905], [88.4727, 26.8845], [88.4718, 26.9015]]
      },
      properties: {
        id: "seg_nh10_005",
        edge_id: "nh10_e_005",
        corridor: "NH-10",
        road_name: "NH-10",
        name: "Sukna to Coronation Bridge (Sevoke)",
        start_node: "Sukna",
        end_node: "Coronation Bridge",
        start_lat: 26.7905,
        start_lon: 88.3615,
        end_lat: 26.9015,
        end_lon: 88.4718,
        length_m: 14200,
        base_travel_time_sec: 1100,
        slope_deg: 12.0,
        river_proximity_m: 120,
        landslide_zone: false,
        historical_incident_count: 4,
        risk_score: 0.28,
        risk_label: "open",
        explanation: "Moderate terrain, no active blockages"
      }
    },
    {
      type: "Feature",
      geometry: {
        type: "LineString",
        coordinates: [[88.4718, 26.9015], [88.4552, 26.9324], [88.4344, 27.0092]]
      },
      properties: {
        id: "seg_nh10_008",
        edge_id: "nh10_e_008",
        corridor: "NH-10",
        road_name: "NH-10",
        name: "Sevoke to Rambi Bazar",
        start_node: "Coronation Bridge",
        end_node: "Rambi Bazar",
        start_lat: 26.9015,
        start_lon: 88.4718,
        end_lat: 27.0092,
        end_lon: 88.4344,
        length_m: 13500,
        base_travel_time_sec: 1400,
        slope_deg: 21.5,
        river_proximity_m: 45,
        landslide_zone: true,
        historical_incident_count: 14,
        risk_score: 0.62,
        risk_label: "risky",
        explanation: "High rain forecast + steep slope & river proximity"
      }
    },
    {
      type: "Feature",
      geometry: {
        type: "LineString",
        coordinates: [[88.4344, 27.0092], [88.4320, 27.0450], [88.4311, 27.0651]]
      },
      properties: {
        id: "seg_nh10_011",
        edge_id: "nh10_e_011",
        corridor: "NH-10",
        road_name: "NH-10",
        name: "29th Mile Landslide Zone (Near Teesta Bazar)",
        start_node: "Rambi Bazar",
        end_node: "Teesta Bazar",
        start_lat: 27.0092,
        start_lon: 88.4344,
        end_lat: 27.0651,
        end_lon: 88.4311,
        length_m: 7200,
        base_travel_time_sec: 900,
        slope_deg: 26.8,
        river_proximity_m: 30,
        landslide_zone: true,
        historical_incident_count: 22,
        risk_score: 1.0,
        risk_label: "blocked",
        explanation: "Blocked by active massive landslide at 29th Mile"
      }
    },
    {
      type: "Feature",
      geometry: {
        type: "LineString",
        coordinates: [[88.4311, 27.0651], [88.4542, 27.0864], [88.5283, 27.1764]]
      },
      properties: {
        id: "seg_nh10_014",
        edge_id: "nh10_e_014",
        corridor: "NH-10",
        road_name: "NH-10",
        name: "Teesta Bazar to Rangpo Checkpost",
        start_node: "Teesta Bazar",
        end_node: "Rangpo Border Gate",
        start_lat: 27.0651,
        start_lon: 88.4311,
        end_lat: 27.1764,
        end_lon: 88.5283,
        length_m: 16800,
        base_travel_time_sec: 1600,
        slope_deg: 18.2,
        river_proximity_m: 60,
        landslide_zone: true,
        historical_incident_count: 9,
        risk_score: 0.54,
        risk_label: "risky",
        explanation: "Shooting stones near Melli Dara"
      }
    },
    {
      type: "Feature",
      geometry: {
        type: "LineString",
        coordinates: [[88.5283, 27.1764], [88.4988, 27.2355], [88.5832, 27.2942], [88.6138, 27.3314]]
      },
      properties: {
        id: "seg_nh10_018",
        edge_id: "nh10_e_018",
        corridor: "NH-10",
        road_name: "NH-10",
        name: "Rangpo to Gangtok Central MG Marg",
        start_node: "Rangpo",
        end_node: "Gangtok MG Marg",
        start_lat: 27.1764,
        start_lon: 88.5283,
        end_lat: 27.3314,
        end_lon: 88.6138,
        length_m: 23500,
        base_travel_time_sec: 2200,
        slope_deg: 14.0,
        river_proximity_m: 180,
        landslide_zone: false,
        historical_incident_count: 3,
        risk_score: 0.22,
        risk_label: "open",
        explanation: "Restored regular traffic flow"
      }
    }
  ]
};

export const FALLBACK_INCIDENTS_NH10: Incident[] = [
  {
    id: "inc_001",
    title: "Massive landslide halts traffic on NH-10 near 29th Mile",
    event_type: "landslide",
    status: "blocked",
    road: "NH-10",
    corridor: "NH-10",
    location_text: "29th Mile Landslide Zone",
    lat: 27.0450,
    lon: 88.4320,
    severity: 5,
    confidence: 0.94,
    confidence_breakdown: {
      source_reliability: 0.95,
      corroboration_count: 0.90,
      geocoding_precision: 0.98,
      recency_decay: 0.92
    },
    provenance: {
      source_url: "https://sikkimexpress.com/news/nh10-massive-landslide-at-29th-mile-traffic-halted",
      domain: "sikkimexpress.com",
      tinyfish_api: "TinyFish Search + Fetch API",
      fetched_at: new Date().toISOString()
    },
    source_count: 2,
    summary: "Vehicular movement between Siliguri and Gangtok on National Highway 10 has been completely suspended following a massive landslide at 29th Mile.",
    evidence_quote: "completely suspended following a massive landslide at 29th Mile early Tuesday morning",
    lifecycle_state: "active",
    verified_by: "District Disaster Control Room",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: "inc_002",
    title: "Subsidence near Kalijhora restricts NH-10 to single lane",
    event_type: "road_closed",
    status: "partially_open",
    road: "NH-10",
    corridor: "NH-10",
    location_text: "Kalijhora Dam",
    lat: 26.9324,
    lon: 88.4552,
    severity: 3,
    confidence: 0.82,
    confidence_breakdown: {
      source_reliability: 0.88,
      corroboration_count: 0.75,
      geocoding_precision: 0.90,
      recency_decay: 0.85
    },
    provenance: {
      source_url: "https://eastmojo.com/sikkim/kalijhora-settlement-subsidence-single-lane-advisory",
      domain: "eastmojo.com",
      tinyfish_api: "TinyFish Search API",
      fetched_at: new Date().toISOString()
    },
    source_count: 1,
    summary: "Single-lane traffic movement near Kalijhora Dam due to road subsidence caused by rising water levels in the Teesta River.",
    evidence_quote: "restricting traffic to single-lane movement near Kalijhora Dam due to road subsidence",
    lifecycle_state: "active",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

export const FALLBACK_ALERTS_NH10: AlertItem[] = [
  {
    id: "alt_001",
    corridor: "NH-10",
    severity: "critical",
    title: "NH-10 Blockage at 29th Mile",
    message: "Massive landslide has cut off NH-10 near 29th Mile. Automatic rerouting calculated via Gorubathan / Lava.",
    incident_id: "inc_001",
    affected_vehicle_ids: ["veh_nh10_01", "veh_nh10_02"],
    suggested_action: "Divert fleet via Lava/Reshi or pause at Sevoke until clearance.",
    created_at: new Date().toISOString()
  }
];

export const FALLBACK_METRICS: MetricsSummary = {
  active_incidents: 4,
  verification_queue_count: 2,
  average_confidence: 0.88,
  blocked_segments: 1,
  routes_rerouted_today: 14,
  model_accuracy_auc: 0.988,
  hotspots: [
    { name: "29th Mile (NH-10)", corridor: "NH-10", risk_level: "blocked", incidents_30d: 18, reason: "Active debris flow & steep slope" },
    { name: "Jorabat Tri-junction (NH-6)", corridor: "NH-6", risk_level: "high_risk", incidents_30d: 14, reason: "Drainage overflow & flood prone" }
  ],
  incidents_by_type: {
    landslide: 8,
    flood: 4,
    waterlogging: 6,
    road_closed: 3
  },
  incidents_by_corridor: {
    "NH-10": 12,
    "NH-6": 9
  }
};
