import React, { useState, useEffect } from 'react';
import { Truck, Navigation, AlertTriangle, ShieldCheck, Clock, MapPin, Smartphone } from 'lucide-react';
import { api, type VehicleItem, type AlertItem } from '../lib/api';

interface FleetAlertsPageProps {
  corridor: string;
  alerts: AlertItem[];
}

export const FleetAlertsPage: React.FC<FleetAlertsPageProps> = ({ corridor, alerts }) => {
  const [vehicles, setVehicles] = useState<VehicleItem[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<VehicleItem | null>(null);

  const fetchVehicles = async () => {
    try {
      const data = await api.getVehicles(corridor);
      setVehicles(data);
      if (data.length > 0 && !selectedVehicle) {
        setSelectedVehicle(data[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchVehicles();
  }, [corridor]);

  // Find active alert affecting selected vehicle
  const activeAlert = alerts.find(a => 
    a.affected_vehicle_ids.includes(selectedVehicle?.id || '')
  ) || alerts[0];

  return (
    <div className="space-y-4 max-w-7xl mx-auto pb-12">
      {/* Page Title */}
      <div className="bg-ridge-darkcard border border-ridge-darkborder p-5 rounded-2xl flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Truck className="w-5 h-5 text-orange-400" />
            <h1 className="text-xl font-bold text-white">Fleet Dispatch & Driver Alert Hub</h1>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Real-time GPS telemetry paired with dynamic hazard alerts and automated cab notifications.
          </p>
        </div>
        <span className="px-3 py-1 bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-xl text-xs font-bold">
          {vehicles.length} Units Active
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left Column: Fleet List (7 cols) */}
        <div className="lg:col-span-7 space-y-3">
          <h2 className="text-xs font-bold text-gray-300 uppercase tracking-wider">
            Active Vehicles on {corridor}
          </h2>
          <div className="space-y-2">
            {vehicles.map((v) => {
              const isSelected = selectedVehicle?.id === v.id;
              const hasAlert = alerts.some(a => a.affected_vehicle_ids.includes(v.id));

              return (
                <div
                  key={v.id}
                  onClick={() => setSelectedVehicle(v)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-ridge-deep border-ridge-orange shadow-lg ring-1 ring-orange-500'
                      : 'bg-ridge-darkcard border-ridge-darkborder hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2.5">
                      <div className={`p-2 rounded-lg ${
                        hasAlert ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        <Truck className="w-4 h-4" />
                      </div>
                      <div>
                        <h3 className="text-xs font-bold text-white">{v.name}</h3>
                        <p className="text-[11px] text-gray-400">{v.type}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      v.status === 'rerouted'
                        ? 'bg-amber-950 text-amber-300 border border-amber-500/30'
                        : 'bg-emerald-950 text-emerald-300 border border-emerald-500/30'
                    }`}>
                      {v.status.toUpperCase()}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px] text-gray-300 pt-2 border-t border-gray-800">
                    <div>Destination: <span className="text-white font-medium">{v.destination}</span></div>
                    <div>Speed: <span className="text-white font-medium">{v.speed_kmh} km/h</span></div>
                  </div>

                  {hasAlert && (
                    <div className="mt-2 text-[10px] bg-red-950/60 border border-red-500/40 p-2 rounded-lg text-red-200 flex items-center gap-1.5 font-medium">
                      <AlertTriangle className="w-3.5 h-3.5 text-red-400 shrink-0" />
                      <span>Route compromised by active road advisory. Reroute active!</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Driver View Panel (5 cols) */}
        <div className="lg:col-span-5">
          <div className="bg-ridge-darkcard border border-ridge-darkborder rounded-2xl p-5 shadow-xl sticky top-20">
            <div className="flex items-center justify-between border-b border-ridge-darkborder pb-3 mb-4">
              <div className="flex items-center gap-2">
                <Smartphone className="w-5 h-5 text-orange-400" />
                <h3 className="text-sm font-bold text-white">Driver In-Cab View</h3>
              </div>
              <span className="text-[10px] font-bold bg-black/40 text-gray-400 px-2 py-0.5 rounded border border-gray-700">
                Tablet HUD
              </span>
            </div>

            {/* Simulated In-Cab High Contrast Display */}
            <div className="bg-black rounded-xl p-5 border-2 border-orange-500/80 shadow-2xl space-y-4">
              <div className="flex justify-between items-center text-xs text-gray-400">
                <span className="font-mono text-orange-400 font-bold">{selectedVehicle?.name || 'VEHICLE 101'}</span>
                <span>{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </div>

              {activeAlert ? (
                <div className="space-y-3">
                  <div className="flex items-center gap-2 p-2.5 bg-red-900/60 border border-red-500 rounded-lg text-red-200 animate-pulse">
                    <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
                    <span className="text-sm font-black uppercase tracking-wider">
                      ROAD ALERT AHEAD
                    </span>
                  </div>

                  <h4 className="text-base font-extrabold text-white leading-snug">
                    {activeAlert.title}
                  </h4>

                  <p className="text-xs text-gray-200 bg-gray-900/80 p-3 rounded-lg border border-gray-700">
                    {activeAlert.message}
                  </p>

                  <div className="p-3 bg-orange-950/70 border border-orange-500 rounded-lg text-xs text-orange-200">
                    <span className="font-bold text-orange-400 uppercase text-[10px] block mb-0.5">
                      Recommended Driver Action:
                    </span>
                    {activeAlert.suggested_action || 'Follow alternative route marked in blue on navigator.'}
                  </div>
                </div>
              ) : (
                <div className="py-8 text-center text-gray-400 text-xs">
                  <ShieldCheck className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
                  <p className="font-bold text-white text-sm">Corridor Clear Ahead</p>
                  <p className="text-[11px] text-gray-500 mt-1">Maintain posted speed limits.</p>
                </div>
              )}

              <div className="pt-3 border-t border-gray-800 flex justify-between text-xs text-gray-400 font-mono">
                <span>DEST: {selectedVehicle?.destination}</span>
                <span className="text-emerald-400 font-bold">RIDGE ACTIVE</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
