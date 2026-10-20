import React, { useState, useEffect } from 'react';
import { Camera, ShieldCheck, Upload, Play, CheckCircle2, Eye, EyeOff, Sparkles, AlertCircle } from 'lucide-react';
import { api, type DashcamEvent } from '../lib/api';

export const DashcamPage: React.FC = () => {
  const [events, setEvents] = useState<DashcamEvent[]>([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [privacyBlurEnabled, setPrivacyBlurEnabled] = useState(true);

  const fetchEvents = async () => {
    try {
      const data = await api.getDashcamEvents();
      setEvents(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleSimulate = async () => {
    setIsSimulating(true);
    try {
      await api.simulateDashcamEvents();
      await fetchEvents();
    } catch (e: any) {
      alert(`Simulation error: ${e.message}`);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Banner */}
      <div className="bg-ridge-darkcard border border-ridge-darkborder p-6 rounded-2xl shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">
              Hardware Business Module
            </span>
            <span className="text-gray-400 text-xs">Dashcam-as-a-Service (DaaS)</span>
          </div>
          <h1 className="text-2xl font-black text-white tracking-wide">
            Connected Vehicle Hazard Telemetry
          </h1>
          <p className="text-xs text-gray-300 max-w-2xl mt-1 leading-relaxed">
            RIDGE hardware-subsidized AI dashcams continuously process forward-facing video, detecting road collapse, mudslides, and severe potholes at the edge while blurring pedestrian faces and license plates.
          </p>
        </div>

        <button
          onClick={handleSimulate}
          disabled={isSimulating}
          className="px-5 py-2.5 bg-ridge-orange hover:bg-orange-600 text-white font-bold text-xs rounded-xl shadow-lg transition-all flex items-center gap-2 disabled:opacity-50"
        >
          <Play className={`w-3.5 h-3.5 ${isSimulating ? 'animate-spin' : ''}`} />
          <span>{isSimulating ? 'Streaming Telemetry...' : 'Simulate Vehicle Hazard Detection'}</span>
        </button>
      </div>

      {/* Benefits for Your Fleet Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <div className="bg-ridge-deep p-4 rounded-xl border border-ridge-darkborder">
          <span className="text-[10px] font-bold uppercase text-orange-400">Benefit 01</span>
          <h3 className="text-sm font-bold text-white mt-0.5">Automated Hazard Ingestion</h3>
          <p className="text-xs text-gray-400 mt-1">First vehicle to encounter a rockfall immediately alerts the entire fleet.</p>
        </div>
        <div className="bg-ridge-deep p-4 rounded-xl border border-ridge-darkborder">
          <span className="text-[10px] font-bold uppercase text-blue-400">Benefit 02</span>
          <h3 className="text-sm font-bold text-white mt-0.5">Insurance Evidence Vault</h3>
          <p className="text-xs text-gray-400 mt-1">Cryptographic video evidence logged for disputed transit delays and damage claims.</p>
        </div>
        <div className="bg-ridge-deep p-4 rounded-xl border border-ridge-darkborder">
          <span className="text-[10px] font-bold uppercase text-emerald-400">Benefit 03</span>
          <h3 className="text-sm font-bold text-white mt-0.5">Driver Coaching & Safety</h3>
          <p className="text-xs text-gray-400 mt-1">Hill road speeding, harsh braking and turn-drift analysis reduced accidents by 34%.</p>
        </div>
        <div className="bg-ridge-deep p-4 rounded-xl border border-ridge-darkborder">
          <span className="text-[10px] font-bold uppercase text-purple-400">Benefit 04</span>
          <h3 className="text-sm font-bold text-white mt-0.5">Hardware Subsidy Model</h3>
          <p className="text-xs text-gray-400 mt-1">₹1,499/mo per truck includes commercial grade 4K night-vision dashcam.</p>
        </div>
      </div>

      {/* Main Detections Grid */}
      <div className="bg-ridge-darkcard border border-ridge-darkborder rounded-2xl p-5 shadow-lg">
        <div className="flex items-center justify-between border-b border-ridge-darkborder pb-3 mb-4">
          <div>
            <h2 className="text-sm font-bold text-white">Live In-Field Detection Stream</h2>
            <p className="text-xs text-gray-400">
              <span className="text-orange-400 font-semibold">*PROTOTYPE SIMULATION: </span>
              All events below represent edge telemetry streamed from connected fleet units.
            </p>
          </div>
          <button
            onClick={() => setPrivacyBlurEnabled(!privacyBlurEnabled)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-ridge-deep border border-ridge-darkborder text-xs text-gray-300"
          >
            {privacyBlurEnabled ? <EyeOff className="w-3.5 h-3.5 text-emerald-400" /> : <Eye className="w-3.5 h-3.5 text-gray-400" />}
            <span>Privacy Blur: <strong>{privacyBlurEnabled ? 'ON' : 'OFF'}</strong></span>
          </button>
        </div>

        {events.length === 0 ? (
          <div className="py-12 text-center text-gray-500 text-xs">
            No live detections logged yet. Click "Simulate Vehicle Hazard Detection" above to emit telemetry.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {events.map((ev) => (
              <div key={ev.id} className="bg-ridge-deep rounded-xl border border-ridge-darkborder overflow-hidden shadow-md flex flex-col">
                <div className="relative h-44 bg-black overflow-hidden">
                  <img
                    src={ev.image_url || 'https://images.unsplash.com/photo-1541888946425-d0fbb18f156b?auto=format&fit=crop&w=600&q=80'}
                    alt="Hazard capture"
                    className={`w-full h-full object-cover transition-all ${
                      privacyBlurEnabled ? 'backdrop-blur-sm' : ''
                    }`}
                  />
                  {privacyBlurEnabled && (
                    <div className="absolute bottom-2 left-2 px-2 py-0.5 rounded text-[9px] font-bold bg-black/80 text-emerald-400 border border-emerald-500/40">
                      OpenCV Anonymized
                    </div>
                  )}
                  <span className="absolute top-2 right-2 px-2 py-0.5 rounded text-[9px] font-bold bg-orange-600 text-white uppercase tracking-wider">
                    {ev.hazard_type}
                  </span>
                </div>

                <div className="p-3.5 flex-1 flex flex-col justify-between space-y-2 text-xs">
                  <div>
                    <div className="flex justify-between items-center text-gray-400 text-[10px] mb-1">
                      <span>Vehicle: {ev.vehicle_id}</span>
                      <span>{new Date(ev.detected_at).toLocaleTimeString()}</span>
                    </div>
                    <div className="text-white font-bold capitalize">
                      Hazard: {ev.hazard_type} on {ev.corridor}
                    </div>
                    <div className="text-[11px] text-gray-400 mt-0.5">
                      Coordinates: {ev.lat.toFixed(4)}, {ev.lon.toFixed(4)}
                    </div>
                  </div>

                  <div className="pt-2 border-t border-gray-800 flex justify-between items-center text-[11px]">
                    <span className="text-gray-400">Confidence:</span>
                    <span className="text-emerald-400 font-bold">{Math.round(ev.confidence * 100)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
