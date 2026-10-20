import React from 'react';
import { 
  ShieldAlert, 
  Layers, 
  Search, 
  CheckCircle2, 
  Truck, 
  Camera, 
  BarChart3, 
  CreditCard,
  RefreshCw,
  ExternalLink
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  selectedCorridor: string;
  setSelectedCorridor: (corridor: string) => void;
  tinyfishMode: string;
  isIngesting: boolean;
  onTriggerIngest: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  selectedCorridor,
  setSelectedCorridor,
  tinyfishMode,
  isIngesting,
  onTriggerIngest
}) => {
  const navItems = [
    { id: 'map', label: 'Live Map', icon: Layers },
    { id: 'pipeline', label: 'TinyFish Pipeline', icon: Search, badge: 'Live AI' },
    { id: 'verify', label: 'Verification Queue', icon: CheckCircle2 },
    { id: 'fleet', label: 'Fleet & Alerts', icon: Truck },
    { id: 'dashcam', label: 'Dashcam DaaS', icon: Camera, badge: 'Hardware' },
    { id: 'insights', label: 'Insights & ML', icon: BarChart3 },
    { id: 'pricing', label: 'Plans & Pricing', icon: CreditCard },
  ];

  return (
    <header className="bg-ridge-deep border-b border-ridge-darkborder sticky top-0 z-50 px-4 py-2.5">
      <div className="flex items-center justify-between gap-4">
        {/* Brand / Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-ridge-orange to-red-600 flex items-center justify-center shadow-lg shadow-orange-500/20">
            <ShieldAlert className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-wider text-white">RIDGE</span>
              <span className="text-[10px] font-semibold bg-ridge-navy/80 text-blue-200 border border-blue-400/30 px-1.5 py-0.5 rounded">
                NER v1.0
              </span>
            </div>
            <p className="text-[11px] text-gray-400 leading-none">
              Regional Intelligence & Geospatial Efficiency
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden lg:flex items-center gap-1 bg-ridge-darkcard p-1 rounded-xl border border-ridge-darkborder">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-ridge-orange text-white shadow-md'
                    : 'text-gray-300 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
                {item.badge && (
                  <span className={`text-[9px] px-1 py-0.2 rounded font-bold ${
                    isActive ? 'bg-black/30 text-white' : 'bg-orange-500/20 text-orange-400'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Right Action Tools: Corridor Switcher, TinyFish Pill, Ingestion Button */}
        <div className="flex items-center gap-3">
          {/* Corridor Switcher */}
          <div className="flex items-center bg-ridge-darkcard rounded-lg border border-ridge-darkborder p-1">
            <button
              onClick={() => setSelectedCorridor('NH-10')}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors ${
                selectedCorridor === 'NH-10'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
              title="Siliguri to Gangtok (West Bengal / Sikkim)"
            >
              NH-10 (Sikkim)
            </button>
            <button
              onClick={() => setSelectedCorridor('NH-6')}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors ${
                selectedCorridor === 'NH-6'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
              title="Guwahati to Shillong (Assam / Meghalaya)"
            >
              NH-6 (Meghalaya)
            </button>
          </div>

          {/* TinyFish Status Badge */}
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-ridge-darkcard border border-ridge-darkborder text-[11px]">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-gray-300">TinyFish:</span>
            <span className="font-semibold text-orange-400 uppercase tracking-wider text-[10px]">
              {tinyfishMode}
            </span>
          </div>

          {/* Trigger Ingestion Button */}
          <button
            onClick={onTriggerIngest}
            disabled={isIngesting}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-ridge-orange hover:bg-orange-600 text-white rounded-lg shadow-md transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isIngesting ? 'animate-spin' : ''}`} />
            <span>{isIngesting ? 'Ingesting...' : 'Run Ingestion'}</span>
          </button>
        </div>
      </div>

      {/* Mobile Nav Bar */}
      <div className="flex lg:hidden overflow-x-auto gap-1 mt-2 pt-2 border-t border-ridge-darkborder scrollbar-none">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs whitespace-nowrap ${
                isActive
                  ? 'bg-ridge-orange text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Icon className="w-3 h-3" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
};
