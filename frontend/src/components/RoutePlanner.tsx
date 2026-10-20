import React, { useState } from 'react';
import { Navigation, ShieldCheck, Zap, Scale, AlertCircle, Clock, MapPin, Check } from 'lucide-react';
import type { RouteResponse, RouteOption } from '../lib/api';

interface RoutePlannerProps {
  corridor: string;
  onCalculateRoute: (origin: string, destination: string, preference: string) => Promise<RouteResponse | null>;
  activeRoute: RouteOption | null;
  setActiveRoute: (route: RouteOption | null) => void;
  isLoading: boolean;
}

export const RoutePlanner: React.FC<RoutePlannerProps> = ({
  corridor,
  onCalculateRoute,
  activeRoute,
  setActiveRoute,
  isLoading
}) => {
  const defaultOrigin = corridor === 'NH-10' ? 'Siliguri Junction' : 'Guwahati Railway Station';
  const defaultDest = corridor === 'NH-10' ? 'Gangtok MG Marg' : 'Police Bazar Roundabout';

  const [origin, setOrigin] = useState(defaultOrigin);
  const [destination, setDestination] = useState(defaultDest);
  const [preference, setPreference] = useState<'safest' | 'fastest' | 'balanced'>('safest');
  const [routeResult, setRouteResult] = useState<RouteResponse | null>(null);

  // Sync defaults when corridor changes
  React.useEffect(() => {
    setOrigin(corridor === 'NH-10' ? 'Siliguri Junction' : 'Guwahati Railway Station');
    setDestination(corridor === 'NH-10' ? 'Gangtok MG Marg' : 'Police Bazar Roundabout');
    setRouteResult(null);
    setActiveRoute(null);
  }, [corridor]);

  const handlePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await onCalculateRoute(origin, destination, preference);
    if (res && res.routes.length > 0) {
      setRouteResult(res);
      setActiveRoute(res.routes[0]);
    }
  };

  return (
    <div className="bg-ridge-darkcard border border-ridge-darkborder rounded-2xl p-4 shadow-xl">
      <div className="flex items-center justify-between border-b border-ridge-darkborder pb-3 mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-blue-500/20 text-blue-400 rounded-lg">
            <Navigation className="w-4 h-4" />
          </div>
          <h3 className="text-sm font-bold text-white">Risk-Aware Route Planner</h3>
        </div>
        <span className="text-[10px] font-bold text-gray-400 uppercase bg-ridge-deep px-2 py-0.5 rounded border border-ridge-darkborder">
          {corridor}
        </span>
      </div>

      <form onSubmit={handlePlan} className="space-y-3">
        {/* Origin */}
        <div>
          <label className="text-[11px] font-medium text-gray-400 block mb-1">Origin Node</label>
          <div className="relative">
            <MapPin className="w-3.5 h-3.5 text-gray-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              className="w-full bg-ridge-deep border border-ridge-darkborder rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-ridge-orange"
              placeholder="e.g. Siliguri Junction"
              required
            />
          </div>
        </div>

        {/* Destination */}
        <div>
          <label className="text-[11px] font-medium text-gray-400 block mb-1">Destination Node</label>
          <div className="relative">
            <MapPin className="w-3.5 h-3.5 text-orange-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              className="w-full bg-ridge-deep border border-ridge-darkborder rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-ridge-orange"
              placeholder="e.g. Gangtok MG Marg"
              required
            />
          </div>
        </div>

        {/* Preference Buttons */}
        <div>
          <label className="text-[11px] font-medium text-gray-400 block mb-1">Optimization Goal</label>
          <div className="grid grid-cols-3 gap-1.5 bg-ridge-deep p-1 rounded-xl border border-ridge-darkborder">
            <button
              type="button"
              onClick={() => setPreference('safest')}
              className={`flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-[11px] font-semibold transition-all ${
                preference === 'safest'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Safest</span>
            </button>

            <button
              type="button"
              onClick={() => setPreference('balanced')}
              className={`flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-[11px] font-semibold transition-all ${
                preference === 'balanced'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Scale className="w-3.5 h-3.5" />
              <span>Balanced</span>
            </button>

            <button
              type="button"
              onClick={() => setPreference('fastest')}
              className={`flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-[11px] font-semibold transition-all ${
                preference === 'fastest'
                  ? 'bg-amber-600 text-white shadow-sm'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Fastest</span>
            </button>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-ridge-orange to-red-600 hover:opacity-90 text-white font-semibold py-2.5 px-4 rounded-xl text-xs shadow-lg shadow-orange-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {isLoading ? (
            <span>Computing Safe Paths...</span>
          ) : (
            <>
              <Navigation className="w-4 h-4" />
              <span>Calculate Safe Route</span>
            </>
          )}
        </button>
      </form>

      {/* Route Results Display */}
      {routeResult && (
        <div className="mt-4 pt-4 border-t border-ridge-darkborder space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-300">Generated Options:</span>
            {routeResult.rerouted_due_to_incident && (
              <span className="text-[10px] bg-red-950/60 text-red-300 border border-red-500/40 px-2 py-0.5 rounded-full font-bold">
                ⚠️ Blockage Rerouted
              </span>
            )}
          </div>

          <div className="space-y-2">
            {routeResult.routes.map((rt) => {
              const isSelected = activeRoute?.route_id === rt.route_id;
              return (
                <div
                  key={rt.route_id}
                  onClick={() => setActiveRoute(rt)}
                  className={`p-3 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-blue-950/30 border-blue-500 shadow-md ring-1 ring-blue-500/50'
                      : 'bg-ridge-deep/60 border-ridge-darkborder hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-xs text-white flex items-center gap-1.5">
                      {isSelected && <Check className="w-3.5 h-3.5 text-blue-400" />}
                      {rt.label}
                    </span>
                    <span className="text-xs font-extrabold text-blue-400">
                      {rt.eta_minutes} mins
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-1 text-[10px] text-gray-400 mb-2">
                    <div>Dist: <span className="text-white font-medium">{rt.distance_km} km</span></div>
                    <div>Avg Risk: <span className="text-emerald-400 font-medium">{(rt.mean_risk * 100).toFixed(0)}%</span></div>
                    <div>Peak Risk: <span className="text-amber-400 font-medium">{(rt.max_risk * 100).toFixed(0)}%</span></div>
                  </div>

                  {/* Plain English Reason */}
                  <div className="p-2 bg-black/40 rounded-lg text-[10px] text-gray-300 border-l-2 border-orange-500">
                    <span className="font-semibold text-orange-400">Why this route: </span>
                    {rt.reason}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
