import React, { useState } from 'react';
import { KPICards } from '../components/KPICards';
import { MapView } from '../components/MapView';
import { RoutePlanner } from '../components/RoutePlanner';
import { AlertsFeed } from '../components/AlertsFeed';
import { 
  GeoJSONFeatureCollection, 
  Incident, 
  AlertItem, 
  MetricsSummary, 
  RouteOption, 
  RouteResponse 
} from '../lib/api';
import { Layers, Eye, EyeOff } from 'lucide-react';

interface LiveMapPageProps {
  corridor: string;
  segments: GeoJSONFeatureCollection | null;
  incidents: Incident[];
  alerts: AlertItem[];
  metrics: MetricsSummary | null;
  onCalculateRoute: (origin: string, destination: string, preference: string) => Promise<RouteResponse | null>;
  activeRoute: RouteOption | null;
  setActiveRoute: (route: RouteOption | null) => void;
  isLoadingRoute: boolean;
}

export const LiveMapPage: React.FC<LiveMapPageProps> = ({
  corridor,
  segments,
  incidents,
  alerts,
  metrics,
  onCalculateRoute,
  activeRoute,
  setActiveRoute,
  isLoadingRoute,
}) => {
  const [showRiskLayer, setShowRiskLayer] = useState(true);
  const [showIncidentsLayer, setShowIncidentsLayer] = useState(true);

  return (
    <div className="flex flex-col gap-3 h-[calc(100vh-80px)]">
      {/* 1. KPI Strip */}
      <KPICards metrics={metrics} selectedCorridor={corridor} />

      {/* 2. Main Grid: Left Route Planner, Center Map, Right Alerts Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 min-h-0">
        {/* Left Column: Route Planner (3 cols) */}
        <div className="lg:col-span-3 overflow-y-auto">
          <RoutePlanner
            corridor={corridor}
            onCalculateRoute={onCalculateRoute}
            activeRoute={activeRoute}
            setActiveRoute={setActiveRoute}
            isLoading={isLoadingRoute}
          />

          {/* Layer Controls */}
          <div className="mt-3 bg-ridge-darkcard border border-ridge-darkborder rounded-xl p-3 text-xs">
            <span className="font-bold text-gray-300 block mb-2 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-blue-400" /> Map Layers
            </span>
            <div className="space-y-1.5">
              <label className="flex items-center justify-between text-gray-300 cursor-pointer">
                <span>Disruption Risk Segments</span>
                <input
                  type="checkbox"
                  checked={showRiskLayer}
                  onChange={(e) => setShowRiskLayer(e.target.checked)}
                  className="rounded text-ridge-orange focus:ring-0"
                />
              </label>
              <label className="flex items-center justify-between text-gray-300 cursor-pointer">
                <span>Active Incident Pins</span>
                <input
                  type="checkbox"
                  checked={showIncidentsLayer}
                  onChange={(e) => setShowIncidentsLayer(e.target.checked)}
                  className="rounded text-ridge-orange focus:ring-0"
                />
              </label>
            </div>
          </div>
        </div>

        {/* Center Column: Interactive Map (6 cols) */}
        <div className="lg:col-span-6 h-full min-h-[420px]">
          <MapView
            corridor={corridor}
            segments={segments}
            incidents={incidents}
            activeRoute={activeRoute}
            showRiskLayer={showRiskLayer}
            showIncidentsLayer={showIncidentsLayer}
          />
        </div>

        {/* Right Column: Live Alerts Feed (3 cols) */}
        <div className="lg:col-span-3 h-full">
          <AlertsFeed alerts={alerts} />
        </div>
      </div>
    </div>
  );
};
