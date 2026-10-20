export interface GeoJSONFeature {
  type: string;
  geometry: {
    type: string;
    coordinates: any;
  };
  properties: {
    id: string;
    edge_id: string;
    corridor: string;
    road_name: string;
    name: string;
    start_node: string;
    end_node: string;
    start_lat: number;
    start_lon: number;
    end_lat: number;
    end_lon: number;
    length_m: number;
    base_travel_time_sec: number;
    slope_deg: number;
    river_proximity_m: number;
    landslide_zone: boolean;
    historical_incident_count: number;
    risk_score: number;
    risk_label: 'open' | 'risky' | 'high_risk' | 'blocked';
    explanation?: string;
  };
}

export interface GeoJSONFeatureCollection {
  type: string;
  features: GeoJSONFeature[];
}

export interface IncidentEvidence {
  id: string;
  source_url: string;
  domain: string;
  snippet: string;
  tinyfish_endpoint: string;
  extracted_at: string;
}

export interface Incident {
  id: string;
  title: string;
  event_type: 'landslide' | 'flood' | 'waterlogging' | 'road_closed' | 'bridge_damage' | 'accident' | 'restored' | 'other';
  status: 'blocked' | 'partially_open' | 'open' | 'unknown';
  road?: string;
  corridor: string;
  location_text: string;
  lat?: number;
  lon?: number;
  severity: number;
  confidence: number;
  confidence_breakdown: {
    source_reliability?: number;
    corroboration_count?: number;
    geocoding_precision?: number;
    recency_decay?: number;
  };
  provenance: {
    source_url?: string;
    domain?: string;
    tinyfish_api?: string;
    fetched_at?: string;
    content_hash?: string;
  };
  source_count: number;
  summary: string;
  evidence_quote?: string;
  lifecycle_state: 'active' | 'monitoring' | 'resolved';
  verified_by?: string;
  verification_note?: string;
  created_at: string;
  updated_at: string;
  evidence?: IncidentEvidence[];
}

export interface GazetteerItem {
  id: string;
  name: string;
  lat: number;
  lon: number;
  corridor: string;
  aliases: string[];
}

export interface RouteOption {
  route_id: string;
  label: string;
  distance_km: number;
  eta_minutes: number;
  mean_risk: number;
  max_risk: number;
  risky_segments_count: number;
  blocked_segments_count: number;
  reason: string;
  coordinates: [number, number][];
  path_nodes: string[];
}

export interface RouteResponse {
  origin: string;
  destination: string;
  preference: string;
  corridor: string;
  routes: RouteOption[];
  rerouted_due_to_incident: boolean;
  plain_english_advice: string;
}

export interface RouteCompareResponse {
  corridor: string;
  origin: string;
  destination: string;
  baseline_route: RouteOption;
  ridge_route: RouteOption;
  risk_reduction_pct: number;
  time_difference_minutes: number;
  explanation: string;
}

export interface AlertItem {
  id: string;
  corridor: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  incident_id?: string;
  affected_vehicle_ids: string[];
  suggested_action?: string;
  created_at: string;
}

export interface VehicleItem {
  id: string;
  name: string;
  type: string;
  corridor: string;
  status: 'in_transit' | 'idle' | 'rerouted' | 'alert';
  current_lat: number;
  current_lon: number;
  destination: string;
  assigned_route_id?: string;
  speed_kmh: number;
  updated_at: string;
}

export interface MetricsSummary {
  active_incidents: number;
  verification_queue_count: number;
  average_confidence: number;
  blocked_segments: number;
  routes_rerouted_today: number;
  model_accuracy_auc: number;
  hotspots: Array<{
    name: string;
    corridor: string;
    risk_level: string;
    incidents_30d: number;
    reason: string;
  }>;
  incidents_by_type: Record<string, number>;
  incidents_by_corridor: Record<string, number>;
}

export interface IngestionStep {
  id: string;
  step_name: string;
  details: Record<string, any>;
  timestamp: string;
}

export interface IngestionRun {
  id: string;
  corridor: string;
  mode: string;
  target_url?: string;
  status: string;
  new_incidents_count: number;
  tinyfish_api_used: string;
  duration_ms: number;
  error_message?: string;
  started_at: string;
  completed_at?: string;
  steps: IngestionStep[];
}

export interface DashcamEvent {
  id: string;
  vehicle_id: string;
  hazard_type: string;
  corridor: string;
  lat: number;
  lon: number;
  confidence: number;
  image_url?: string;
  is_simulated: boolean;
  incident_id?: string;
  detected_at: string;
}

const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error [${res.status}]: ${errorText || res.statusText}`);
  }
  return res.json();
}

export const api = {
  getHealth: () => request<any>('/health'),
  
  getRiskSegments: (corridor?: string) => 
    request<GeoJSONFeatureCollection>(`/risk/segments${corridor ? `?corridor=${corridor}` : ''}`),
  
  getIncidents: (params?: { corridor?: string; status?: string; min_confidence?: number; max_confidence?: number }) => {
    const query = new URLSearchParams();
    if (params?.corridor) query.set('corridor', params.corridor);
    if (params?.status) query.set('status', params.status);
    if (params?.min_confidence !== undefined) query.set('min_confidence', params.min_confidence.toString());
    if (params?.max_confidence !== undefined) query.set('max_confidence', params.max_confidence.toString());
    const qs = query.toString();
    return request<Incident[]>(`/incidents${qs ? `?${qs}` : ''}`);
  },

  getIncident: (id: string) => request<Incident>(`/incidents/${id}`),

  verifyIncident: (id: string, payload: { decision: 'confirm' | 'reject'; note?: string; verifier?: string }) =>
    request<Incident>(`/incidents/${id}/verify`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getGazetteer: (corridor?: string, query?: string) => {
    const sp = new URLSearchParams();
    if (corridor) sp.set('corridor', corridor);
    if (query) sp.set('query', query);
    const qs = sp.toString();
    return request<GazetteerItem[]>(`/gazetteer${qs ? `?${qs}` : ''}`);
  },

  getMetricsSummary: () => request<MetricsSummary>('/metrics/summary'),

  calculateRoutes: (payload: { origin: string; destination: string; preference?: string; corridor?: string }) =>
    request<RouteResponse>('/routes', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  compareRoutes: (origin?: string, destination?: string, corridor?: string) => {
    const sp = new URLSearchParams();
    if (origin) sp.set('origin', origin);
    if (destination) sp.set('destination', destination);
    if (corridor) sp.set('corridor', corridor);
    const qs = sp.toString();
    return request<RouteCompareResponse>(`/routes/compare${qs ? `?${qs}` : ''}`);
  },

  getAlerts: (corridor?: string) =>
    request<AlertItem[]>(`/alerts${corridor ? `?corridor=${corridor}` : ''}`),

  getVehicles: (corridor?: string) =>
    request<VehicleItem[]>(`/fleet/vehicles${corridor ? `?corridor=${corridor}` : ''}`),

  triggerIngestion: (payload: { corridor: string; mode: 'search' | 'url'; url?: string }) =>
    request<{ run_id: string; message: string }>('/ingestion/run', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getIngestionRuns: (limit = 10) =>
    request<IngestionRun[]>(`/ingestion/runs?limit=${limit}`),

  getIngestionRun: (id: string) =>
    request<IngestionRun>(`/ingestion/runs/${id}`),

  getDashcamEvents: () =>
    request<DashcamEvent[]>('/dashcam/events'),

  simulateDashcamEvents: () =>
    request<DashcamEvent[]>('/dashcam/simulate', { method: 'POST' }),
};
