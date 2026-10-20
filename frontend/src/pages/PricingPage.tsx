import React from 'react';
import { Check, CreditCard, Sparkles, Truck, ShieldCheck, Zap } from 'lucide-react';

export const PricingPage: React.FC = () => {
  const plans = [
    {
      name: 'Starter Telemetry',
      price: '₹999',
      period: 'per vehicle / month',
      description: 'Ideal for small logistics operators with existing Android devices or basic trackers.',
      features: [
        'TinyFish Live Disruption Alerts',
        'Dynamic Risk-Weighted Routing',
        'Authority Verification Queue Access',
        'Standard Corridor Insights',
        'WhatsApp Driver Alerts'
      ],
      highlighted: false,
      cta: 'Start 14-Day Pilot'
    },
    {
      name: 'Pro Dashcam DaaS',
      price: '₹1,499',
      period: 'per vehicle / month',
      badge: 'Most Popular • Hardware Included',
      description: 'Complete commercial package: 4K Night-Vision AI Dashcam supplied with hardware warranty.',
      features: [
        'All Starter Telemetry Features',
        'Supplied 4K AI Road-Facing Dashcam',
        'Edge Rockfall & Flood Detection',
        'OpenCV Automated Privacy Anonymization',
        'Insurance Vault Video Storage',
        'Automated In-Cab Driver Tablet HUD',
        'Guaranteed 24/7 Corridor Support'
      ],
      highlighted: true,
      cta: 'Deploy Fleet Trial'
    },
    {
      name: 'Enterprise / Authority',
      price: 'Custom',
      period: 'annual enterprise agreement',
      description: 'For state disaster authorities, BRO, NHIDCL, and corporate fleets over 50+ vehicles.',
      features: [
        'Dedicated PostGIS Risk API Stream',
        'Custom Web Intelligence Crawl Targets',
        'High-Resolution Satellite Data Overlay',
        'Multi-Tenant Dispatcher Console',
        'Custom XGBoost Model Retraining',
        'Dedicated SLA & On-Premise Air-Gap Option'
      ],
      highlighted: false,
      cta: 'Contact Solutions Team'
    }
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16">
      {/* Page Title */}
      <div className="text-center space-y-3 max-w-3xl mx-auto pt-4">
        <span className="px-3 py-1 rounded-full text-xs font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">
          Hardware-Subsidized Subscription Model
        </span>
        <h1 className="text-3xl font-black text-white tracking-wide">
          Dashcam-as-a-Service (DaaS) Pricing
        </h1>
        <p className="text-sm text-gray-300 leading-relaxed">
          Zero upfront capital expense for fleet operators. We provide commercial grade AI dashcams that stream live road conditions back into the public safety network.
        </p>
      </div>

      {/* Pricing Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((p, idx) => (
          <div
            key={idx}
            className={`p-6 rounded-2xl border flex flex-col justify-between transition-all ${
              p.highlighted
                ? 'bg-gradient-to-b from-ridge-navy to-ridge-deep border-ridge-orange shadow-2xl shadow-orange-500/20 ring-2 ring-ridge-orange relative'
                : 'bg-ridge-darkcard border-ridge-darkborder'
            }`}
          >
            {p.badge && (
              <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-ridge-orange text-white shadow-md">
                {p.badge}
              </span>
            )}

            <div>
              <h3 className="text-lg font-bold text-white">{p.name}</h3>
              <p className="text-xs text-gray-400 mt-1 min-h-[36px]">{p.description}</p>

              <div className="my-5 pb-5 border-b border-ridge-darkborder">
                <span className="text-3xl font-black text-white">{p.price}</span>
                <span className="text-xs text-gray-400 ml-2">{p.period}</span>
              </div>

              <div className="space-y-2.5 mb-6">
                <span className="text-xs font-bold text-gray-300 uppercase tracking-wide block mb-1">
                  What's Included:
                </span>
                {p.features.map((f, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-gray-300">
                    <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <span>{f}</span>
                  </div>
                ))}
              </div>
            </div>

            <button
              className={`w-full py-3 rounded-xl font-bold text-xs shadow-md transition-all ${
                p.highlighted
                  ? 'bg-ridge-orange hover:bg-orange-600 text-white shadow-orange-500/30'
                  : 'bg-ridge-deep hover:bg-gray-800 text-gray-200 border border-ridge-darkborder'
              }`}
            >
              {p.cta}
            </button>
          </div>
        ))}
      </div>

      {/* Why These Prices & Market Economics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Box 1: Market Benchmarks */}
        <div className="bg-ridge-darkcard border border-ridge-darkborder p-5 rounded-2xl shadow-lg space-y-2 text-xs">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Zap className="w-4 h-4 text-orange-400" />
            Why These Prices? (Industry Benchmarks)
          </h3>
          <ul className="space-y-2 text-gray-300 pt-2">
            <li>
              • <strong>Lease Comparison:</strong> Competitor Dacio.ai leases AI dashcams at ~₹2,000/mo. RIDGE Pro offers full AI road hazard intelligence at ₹1,499/mo.
            </li>
            <li>
              • <strong>CapEx Elimination:</strong> Buying an AI dashcam outright costs ₹35,000 - ₹75,000 upfront. A 36-month Pro plan totals ₹53,964 including all cloud analytics, updates and warranty.
            </li>
            <li>
              • <strong>SME Heavy Market:</strong> Over 75% of commercial freight vehicles in India belong to small and mid-sized operators with under 5 trucks who cannot afford CapEx.
            </li>
            <li>
              • <strong>Growing Market:</strong> India's fleet management market is projected at $4.79B by FY32 growing at 15.25% CAGR.
            </li>
          </ul>
        </div>

        {/* Box 2: Unit Economics */}
        <div className="bg-ridge-darkcard border border-ridge-darkborder p-5 rounded-2xl shadow-lg space-y-2 text-xs">
          <div className="flex items-center justify-between border-b border-ridge-darkborder pb-2">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-emerald-400" />
              Unit Economics (Per Vehicle)
            </h3>
            <span className="text-[10px] text-gray-400 italic">Pilot Projections</span>
          </div>
          <div className="grid grid-cols-2 gap-3 pt-2 text-gray-300">
            <div className="p-3 bg-ridge-deep rounded-xl border border-ridge-darkborder">
              <span className="text-gray-400 block text-[10px] uppercase font-bold">Hardware Bill of Materials</span>
              <span className="text-base font-extrabold text-white mt-1 block">₹8,000</span>
              <span className="text-[10px] text-gray-400">4K Sensor + Edge NPU Module</span>
            </div>
            <div className="p-3 bg-ridge-deep rounded-xl border border-ridge-darkborder">
              <span className="text-gray-400 block text-[10px] uppercase font-bold">Cloud & Telemetry Opex</span>
              <span className="text-base font-extrabold text-white mt-1 block">₹300 / mo</span>
              <span className="text-[10px] text-gray-400">TinyFish API + 4G SIM data</span>
            </div>
            <div className="p-3 bg-ridge-deep rounded-xl border border-ridge-darkborder">
              <span className="text-gray-400 block text-[10px] uppercase font-bold">Monthly Net Margin</span>
              <span className="text-base font-extrabold text-emerald-400 mt-1 block">₹1,199 / mo</span>
              <span className="text-[10px] text-gray-400">Gross margin ~80%</span>
            </div>
            <div className="p-3 bg-ridge-deep rounded-xl border border-ridge-darkborder">
              <span className="text-gray-400 block text-[10px] uppercase font-bold">Hardware Payback Period</span>
              <span className="text-base font-extrabold text-orange-400 mt-1 block">~6.7 Months</span>
              <span className="text-[10px] text-gray-400">Profitable thereafter</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
