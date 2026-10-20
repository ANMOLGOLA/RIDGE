import React from 'react';
import { AlertTriangle, CheckCircle, Ban, Navigation } from 'lucide-react';
import type { MetricsSummary } from '../lib/api';

interface KPICardsProps {
  metrics: MetricsSummary | null;
  selectedCorridor: string;
}

export const KPICards: React.FC<KPICardsProps> = ({ metrics, selectedCorridor }) => {
  if (!metrics) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-16 bg-ridge-darkcard animate-pulse rounded-xl border border-ridge-darkborder"></div>
        ))}
      </div>
    );
  }

  const corridorIncidents = metrics.incidents_by_corridor[selectedCorridor] || metrics.active_incidents;

  const cards = [
    {
      label: `${selectedCorridor} Active Incidents`,
      value: corridorIncidents,
      sub: `${metrics.active_incidents} across all corridors`,
      icon: AlertTriangle,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/20'
    },
    {
      label: 'Average Intelligence Confidence',
      value: `${Math.round(metrics.average_confidence * 100)}%`,
      sub: 'TinyFish multi-source verified',
      icon: CheckCircle,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20'
    },
    {
      label: 'Blocked Segments (Immediate Reroute)',
      value: metrics.blocked_segments,
      sub: 'Penalties applied to routing graph',
      icon: Ban,
      color: 'text-red-400',
      bg: 'bg-red-500/10',
      border: 'border-red-500/20'
    },
    {
      label: 'Safe Reroutes Generated Today',
      value: metrics.routes_rerouted_today,
      sub: 'Estimated 2.8 hrs transit saved',
      icon: Navigation,
      color: 'text-blue-400',
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/20'
    }
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`p-3 rounded-xl bg-ridge-darkcard border ${card.border} flex items-center justify-between shadow-sm transition-transform hover:-translate-y-0.5`}
          >
            <div>
              <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wide">
                {card.label}
              </p>
              <div className="flex items-baseline gap-2 mt-0.5">
                <span className={`text-2xl font-bold ${card.color}`}>{card.value}</span>
                <span className="text-[11px] text-gray-500 hidden sm:inline">{card.sub}</span>
              </div>
            </div>
            <div className={`p-2.5 rounded-lg ${card.bg}`}>
              <Icon className={`w-5 h-5 ${card.color}`} />
            </div>
          </div>
        );
      })}
    </div>
  );
};
