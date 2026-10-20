import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { LiveMapPage } from './pages/LiveMapPage';
import { TinyFishPipelinePage } from './pages/TinyFishPipelinePage';
import { VerificationQueuePage } from './pages/VerificationQueuePage';
import { FleetAlertsPage } from './pages/FleetAlertsPage';
import { DashcamPage } from './pages/DashcamPage';
import { InsightsPage } from './pages/InsightsPage';
import { PricingPage } from './pages/PricingPage';
import { 
  api, 
  type GeoJSONFeatureCollection, 
  type Incident, 
  type AlertItem, 
  type MetricsSummary, 
  type RouteOption, 
  type RouteResponse 
} from './lib/api';

import { 
  FALLBACK_SEGMENTS_NH10, 
  FALLBACK_INCIDENTS_NH10, 
  FALLBACK_ALERTS_NH10, 
  FALLBACK_METRICS 
} from './lib/fallbackData';

function App() {
  const [activeTab, setActiveTab] = useState('map');
  const [corridor, setCorridor] = useState('NH-10');
  const [tinyfishMode, setTinyfishMode] = useState('fixture');
  const [isIngesting, setIsIngesting] = useState(false);

  // Core Data States (Initialized with fallback data so UI renders immediately)
  const [segments, setSegments] = useState<GeoJSONFeatureCollection | null>(FALLBACK_SEGMENTS_NH10);
  const [incidents, setIncidents] = useState<Incident[]>(FALLBACK_INCIDENTS_NH10);
  const [alerts, setAlerts] = useState<AlertItem[]>(FALLBACK_ALERTS_NH10);
  const [metrics, setMetrics] = useState<MetricsSummary | null>(FALLBACK_METRICS);
  const [activeRoute, setActiveRoute] = useState<RouteOption | null>(null);
  const [isLoadingRoute, setIsLoadingRoute] = useState(false);

  // Load Initial Health & Data
  const loadData = async () => {
    try {
      const [health, segData, incData, altData, metData] = await Promise.all([
        api.getHealth(),
        api.getRiskSegments(corridor),
        api.getIncidents({ corridor }),
        api.getAlerts(corridor),
        api.getMetricsSummary()
      ]);

      if (health?.tinyfish_mode) {
        setTinyfishMode(health.tinyfish_mode);
      }
      if (segData?.features?.length) setSegments(segData);
      if (incData?.length) setIncidents(incData);
      if (altData?.length) setAlerts(altData);
      if (metData) setMetrics(metData);
    } catch (err) {
      console.warn('Backend API connecting (using local intelligence cache):', err);
    }
  };

  useEffect(() => {
    loadData();
    // Poll updates every 20 seconds
    const interval = setInterval(loadData, 20000);
    return () => clearInterval(interval);
  }, [corridor]);

  // Handle Manual Ingestion Run
  const handleTriggerIngest = async () => {
    setIsIngesting(true);
    try {
      await api.triggerIngestion({ corridor, mode: 'search' });
      await loadData();
    } catch (err: any) {
      alert(`Ingestion run error: ${err.message}`);
    } finally {
      setIsIngesting(false);
    }
  };

  // Handle Route Calculation
  const handleCalculateRoute = async (
    origin: string,
    destination: string,
    preference: string
  ): Promise<RouteResponse | null> => {
    setIsLoadingRoute(true);
    try {
      const res = await api.calculateRoutes({
        origin,
        destination,
        preference,
        corridor
      });
      return res;
    } catch (err: any) {
      alert(`Routing calculation error: ${err.message}`);
      return null;
    } finally {
      setIsLoadingRoute(false);
    }
  };

  return (
    <div className="min-h-screen bg-ridge-darkbg text-gray-100 flex flex-col font-sans">
      {/* 1. Global Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        selectedCorridor={corridor}
        setSelectedCorridor={setCorridor}
        tinyfishMode={tinyfishMode}
        isIngesting={isIngesting}
        onTriggerIngest={handleTriggerIngest}
      />

      {/* 2. Main Page Views */}
      <main className="flex-1 p-3 lg:p-4 overflow-y-auto">
        {activeTab === 'map' && (
          <LiveMapPage
            corridor={corridor}
            segments={segments}
            incidents={incidents}
            alerts={alerts}
            metrics={metrics}
            onCalculateRoute={handleCalculateRoute}
            activeRoute={activeRoute}
            setActiveRoute={setActiveRoute}
            isLoadingRoute={isLoadingRoute}
          />
        )}

        {activeTab === 'pipeline' && (
          <TinyFishPipelinePage
            corridor={corridor}
            onNavigateToMap={() => setActiveTab('map')}
          />
        )}

        {activeTab === 'verify' && (
          <VerificationQueuePage corridor={corridor} />
        )}

        {activeTab === 'fleet' && (
          <FleetAlertsPage corridor={corridor} alerts={alerts} />
        )}

        {activeTab === 'dashcam' && (
          <DashcamPage />
        )}

        {activeTab === 'insights' && (
          <InsightsPage />
        )}

        {activeTab === 'pricing' && (
          <PricingPage />
        )}
      </main>

      {/* 3. Global Footer with Transparency Disclosure */}
      <footer className="bg-ridge-deep border-t border-ridge-darkborder px-4 py-2.5 text-center text-xs text-gray-400 flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="font-bold text-white tracking-wide">RIDGE</span>
          <span>• Regional Intelligence & Geospatial Efficiency</span>
        </div>
        <div className="text-[11px] text-gray-400">
          <span className="text-orange-400 font-semibold">*Transparency Disclosure: </span>
          Disruption ML model trained on synthetic geomorphological data for the prototype. Replace with historical incident data for production.
        </div>
        <div className="text-[11px] text-gray-500">
          KRITICAL HACKS'26 • Team VISTAARX
        </div>
      </footer>
    </div>
  );
}

export default App;
