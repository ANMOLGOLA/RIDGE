import React from 'react';
import { AlertCircle, Bell, ArrowRight, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { AlertItem } from '../lib/api';

interface AlertsFeedProps {
  alerts: AlertItem[];
  onSelectAlert?: (alert: AlertItem) => void;
}

export const AlertsFeed: React.FC<AlertsFeedProps> = ({ alerts, onSelectAlert }) => {
  return (
    <div className="bg-ridge-darkcard border border-ridge-darkborder rounded-2xl p-4 flex flex-col h-full shadow-lg">
      <div className="flex items-center justify-between border-b border-ridge-darkborder pb-3 mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-orange-500/20 text-orange-400 rounded-lg">
            <Bell className="w-4 h-4 animate-bounce" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Live Disruption Feed</h3>
            <p className="text-[10px] text-gray-400">Real-time corridor advisories & reroutes</p>
          </div>
        </div>
        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
          SSE Active
        </span>
      </div>

      <div className="space-y-3 overflow-y-auto flex-1 pr-1">
        {alerts.length === 0 ? (
          <div className="text-center py-10 text-gray-500 text-xs">
            <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-gray-600" />
            No active disruption alerts on this corridor.
          </div>
        ) : (
          alerts.map((alt) => (
            <div
              key={alt.id}
              onClick={() => onSelectAlert?.(alt)}
              className={`p-3 rounded-xl border transition-all cursor-pointer ${
                alt.severity === 'critical'
                  ? 'bg-red-950/20 border-red-500/30 hover:border-red-500/60'
                  : 'bg-ridge-deep/60 border-ridge-darkborder hover:border-orange-500/50'
              }`}
            >
              <div className="flex items-center justify-between gap-1 mb-1">
                <span className={`px-2 py-0.5 rounded text-[9px] font-bold tracking-wider uppercase ${
                  alt.severity === 'critical'
                    ? 'bg-red-600 text-white'
                    : alt.severity === 'high'
                    ? 'bg-amber-600 text-white'
                    : 'bg-blue-600 text-white'
                }`}>
                  {alt.severity}
                </span>
                <span className="text-[10px] text-gray-400">
                  {new Date(alt.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>

              <h4 className="text-xs font-bold text-white mb-1 line-clamp-1">
                {alt.title}
              </h4>
              <p className="text-[11px] text-gray-300 leading-relaxed line-clamp-2 mb-2">
                {alt.message}
              </p>

              {alt.suggested_action && (
                <div className="bg-black/30 p-2 rounded-lg text-[10px] text-orange-200 border-l-2 border-orange-500 mb-2">
                  <span className="font-semibold text-orange-400">Action: </span>
                  {alt.suggested_action}
                </div>
              )}

              {alt.affected_vehicle_ids.length > 0 && (
                <div className="text-[10px] text-gray-400 flex items-center justify-between pt-1 border-t border-gray-800">
                  <span>Affected: {alt.affected_vehicle_ids.length} fleet unit(s)</span>
                  <span className="text-blue-400 flex items-center gap-0.5 hover:underline">
                    Inspect <ArrowRight className="w-2.5 h-2.5" />
                  </span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
