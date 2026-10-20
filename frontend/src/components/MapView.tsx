import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { 
  AlertTriangle, 
  Droplets, 
  Ban, 
  ExternalLink, 
  ShieldCheck, 
  Clock, 
  Flame, 
  Navigation,
  Info
} from 'lucide-react';
import { GeoJSONFeatureCollection, Incident, RouteOption } from '../lib/api';

// Center changer helper
function ChangeView({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: true });
  }, [center, zoom, map]);
  return null;
}

interface MapViewProps {
  corridor: string;
  segments: GeoJSONFeatureCollection | null;
  incidents: Incident[];
  activeRoute: RouteOption | null;
  onSelectIncident?: (incident: Incident) => void;
  showRiskLayer?: boolean;
  showIncidentsLayer?: boolean;
}

export const MapView: React.FC<MapViewProps> = ({
  corridor,
  segments,
  incidents,
  activeRoute,
  onSelectIncident,
  showRiskLayer = true,
  showIncidentsLayer = true,
}) => {
  const center: [number, number] = corridor === 'NH-10' 
    ? [27.05, 88.48] 
    : [25.88, 91.88];
  const zoom = 10;

  // Segment styling based on risk label
  const getSegmentColor = (riskLabel: string, riskScore: number) => {
    if (riskLabel === 'blocked' || riskScore >= 0.95) return '#111827'; // Dark Black
    if (riskLabel === 'high_risk' || riskScore > 0.65) return '#EF4444'; // Red
    if (riskLabel === 'risky' || riskScore >= 0.35) return '#F59E0B'; // Amber
    return '#10B981'; // Green
  };

  // Custom Leaflet DivIcon for Incidents
  const createIncidentIcon = (incident: Incident) => {
    let bgColor = 'bg-amber-500';
    let iconChar = '⚠️';
    if (incident.status === 'blocked') {
      bgColor = 'bg-red-600 animate-pulse';
      iconChar = '🚫';
    } else if (incident.event_type === 'landslide') {
      bgColor = 'bg-red-500';
      iconChar = '⛰️';
    } else if (incident.event_type === 'flood' || incident.event_type === 'waterlogging') {
      bgColor = 'bg-blue-500';
      iconChar = '🌊';
    }

    return L.divIcon({
      className: 'custom-leaflet-marker',
      html: `
        <div style="
          background-color: ${incident.status === 'blocked' ? '#DC2626' : '#F97316'};
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 2px solid white;
          box-shadow: 0 4px 10px rgba(0,0,0,0.5);
          font-size: 15px;
          cursor: pointer;
        ">
          ${iconChar}
        </div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    });
  };

  return (
    <div className="relative w-full h-full rounded-2xl overflow-hidden border border-ridge-darkborder shadow-2xl">
      {/* Map Legend */}
      <div className="absolute top-4 right-4 z-[1000] bg-ridge-darkcard/90 backdrop-blur-md border border-ridge-darkborder p-3 rounded-xl shadow-lg text-xs space-y-1.5 pointer-events-auto">
        <div className="font-bold text-gray-200 border-b border-ridge-darkborder pb-1 mb-1.5 flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-orange-400" />
          <span>Disruption Risk Legend</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3.5 h-1 rounded bg-[#10B981]"></span>
          <span className="text-gray-300">Open (&lt; 0.35)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3.5 h-1 rounded bg-[#F59E0B]"></span>
          <span className="text-gray-300">Moderate Risk (0.35 - 0.65)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3.5 h-1 rounded bg-[#EF4444]"></span>
          <span className="text-gray-300">High Disruption Risk (&gt; 0.65)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3.5 h-1.5 rounded bg-[#111827] border border-red-500"></span>
          <span className="text-gray-300 font-semibold text-red-400">Confirmed Blocked</span>
        </div>
        {activeRoute && (
          <div className="pt-1.5 border-t border-ridge-darkborder flex items-center gap-2">
            <span className="w-3.5 h-1.5 rounded bg-blue-500 animate-pulse"></span>
            <span className="text-blue-300 font-medium">Active Recommended Route</span>
          </div>
        )}
      </div>

      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <ChangeView center={center} zoom={zoom} />

        {/* Dark Modern Basemap */}
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />

        {/* 1. Road Segments Layer */}
        {showRiskLayer && segments?.features.map((feat) => {
          const coords = feat.geometry.coordinates.map((c: [number, number]) => [c[1], c[0]] as [number, number]);
          const riskColor = getSegmentColor(feat.properties.risk_label, feat.properties.risk_score);
          const isBlocked = feat.properties.risk_label === 'blocked';

          return (
            <Polyline
              key={feat.properties.id}
              positions={coords}
              pathOptions={{
                color: riskColor,
                weight: isBlocked ? 6 : 4.5,
                opacity: 0.9,
                dashArray: isBlocked ? '8, 8' : undefined
              }}
            >
              <Popup>
                <div className="p-1 space-y-2 text-xs text-white max-w-xs">
                  <div className="font-bold text-sm text-orange-400 border-b border-gray-700 pb-1">
                    {feat.properties.name}
                  </div>
                  <div className="grid grid-cols-2 gap-1 text-[11px] text-gray-300">
                    <div>Road: <span className="text-white font-medium">{feat.properties.road_name}</span></div>
                    <div>Length: <span className="text-white font-medium">{(feat.properties.length_m / 1000).toFixed(1)} km</span></div>
                    <div>Slope: <span className="text-white font-medium">{feat.properties.slope_deg}°</span></div>
                    <div>River Proximity: <span className="text-white font-medium">{feat.properties.river_proximity_m} m</span></div>
                  </div>
                  <div className="p-2 rounded bg-black/40 border border-gray-700 mt-1">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-gray-400">Risk Assessment:</span>
                      <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${
                        isBlocked ? 'bg-red-900/60 text-red-200 border border-red-500' :
                        feat.properties.risk_score > 0.65 ? 'bg-red-800/40 text-red-300' :
                        feat.properties.risk_score >= 0.35 ? 'bg-amber-800/40 text-amber-300' :
                        'bg-emerald-800/40 text-emerald-300'
                      }`}>
                        {feat.properties.risk_label.toUpperCase()} ({Math.round(feat.properties.risk_score * 100)}%)
                      </span>
                    </div>
                    <p className="text-[11px] text-gray-300 italic">
                      "{feat.properties.explanation || 'Normal transit parameters'}"
                    </p>
                  </div>
                </div>
              </Popup>
            </Polyline>
          );
        })}

        {/* 2. Active Route Layer (if calculated) */}
        {activeRoute && (
          <Polyline
            positions={activeRoute.coordinates.map((c: [number, number]) => [c[1], c[0]] as [number, number])}
            pathOptions={{
              color: '#3B82F6',
              weight: 6,
              opacity: 0.95,
            }}
          />
        )}

        {/* 3. Incidents Markers */}
        {showIncidentsLayer && incidents.map((inc) => {
          if (!inc.lat || !inc.lon) return null;
          return (
            <Marker
              key={inc.id}
              position={[inc.lat, inc.lon]}
              icon={createIncidentIcon(inc)}
              eventHandlers={{
                click: () => onSelectIncident?.(inc)
              }}
            >
              <Popup>
                <div className="p-2 text-xs text-white max-w-sm space-y-2">
                  <div className="flex items-center justify-between gap-2 border-b border-gray-700 pb-1.5">
                    <span className="font-bold text-sm text-orange-400">
                      {inc.title}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      inc.status === 'blocked' ? 'bg-red-600 text-white' : 'bg-amber-500/80 text-black'
                    }`}>
                      {inc.status.toUpperCase()}
                    </span>
                  </div>

                  <p className="text-gray-300 text-xs leading-relaxed">
                    {inc.summary}
                  </p>

                  {inc.evidence_quote && (
                    <div className="p-2 rounded bg-black/50 border-l-2 border-orange-500 text-[11px] text-orange-200 italic">
                      "{inc.evidence_quote}"
                    </div>
                  )}

                  <div className="pt-2 border-t border-gray-700 space-y-1 text-[11px]">
                    <div className="flex justify-between text-gray-400">
                      <span>Intelligence Confidence:</span>
                      <span className="text-emerald-400 font-bold">
                        {Math.round(inc.confidence * 100)}%
                      </span>
                    </div>
                    <div className="flex justify-between text-gray-400">
                      <span>Source:</span>
                      <a 
                        href={inc.provenance.source_url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="text-blue-400 hover:underline flex items-center gap-1"
                      >
                        {inc.provenance.domain || 'Source Link'}
                        <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    </div>
                    <div className="flex justify-between text-gray-400">
                      <span>Verification Status:</span>
                      <span className={inc.verified_by ? 'text-emerald-400' : 'text-amber-400'}>
                        {inc.verified_by ? `Verified (${inc.verified_by})` : 'Pending Authority Review'}
                      </span>
                    </div>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};
