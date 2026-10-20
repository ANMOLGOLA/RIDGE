import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Download, 
  Cpu, 
  MapPin, 
  ShieldAlert, 
  ExternalLink, 
  Play, 
  CheckCircle2, 
  Clock, 
  Sparkles,
  Link as LinkIcon
} from 'lucide-react';
import { IngestionRun, api } from '../lib/api';

interface TinyFishPipelinePageProps {
  corridor: string;
  onNavigateToMap: () => void;
}

export const TinyFishPipelinePage: React.FC<TinyFishPipelinePageProps> = ({
  corridor,
  onNavigateToMap
}) => {
  const [pasteUrl, setPasteUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [liveLog, setLiveLog] = useState<any[]>([]);
  const [recentRuns, setRecentRuns] = useState<IngestionRun[]>([]);
  const [createdIncidentId, setCreatedIncidentId] = useState<string | null>(null);

  const steps = [
    { id: 'search', name: '1. Discover (Search API)', icon: Search, desc: 'Corridor search query across public bulletins' },
    { id: 'fetch', name: '2. Read (Fetch API)', icon: Download, desc: 'JavaScript rendering & clean markdown extraction' },
    { id: 'extract', name: '3. Parse & Validate', icon: Cpu, desc: 'Pydantic structure validation & NLP classification' },
    { id: 'geocode', name: '4. Gazetteer Geocoding', icon: MapPin, desc: 'Fuzzy match & edge snapping (<500m)' },
    { id: 'incident', name: '5. Incident & Provenance', icon: ShieldAlert, desc: 'Multi-factor confidence scoring & map emit' },
  ];

  const fetchRuns = async () => {
    try {
      const runs = await api.getIngestionRuns(10);
      setRecentRuns(runs);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchRuns();
    // Connect to SSE stream
    const eventSource = new EventSource('http://localhost:8000/api/stream/pipeline');
    
    eventSource.addEventListener('search_started', (e: any) => {
      setActiveStepIndex(0);
      setLiveLog(prev => [{ stage: 'Search', data: JSON.parse(e.data), time: new Date() }, ...prev]);
    });
    eventSource.addEventListener('results_found', (e: any) => {
      setActiveStepIndex(1);
      setLiveLog(prev => [{ stage: 'Results Found', data: JSON.parse(e.data), time: new Date() }, ...prev]);
    });
    eventSource.addEventListener('fetch_done', (e: any) => {
      setActiveStepIndex(2);
      setLiveLog(prev => [{ stage: 'Fetch Done', data: JSON.parse(e.data), time: new Date() }, ...prev]);
    });
    eventSource.addEventListener('extracted', (e: any) => {
      setActiveStepIndex(3);
      setLiveLog(prev => [{ stage: 'Extracted Event', data: JSON.parse(e.data), time: new Date() }, ...prev]);
    });
    eventSource.addEventListener('geocoded', (e: any) => {
      setActiveStepIndex(4);
      setLiveLog(prev => [{ stage: 'Geocoded Location', data: JSON.parse(e.data), time: new Date() }, ...prev]);
    });
    eventSource.addEventListener('incident_created', (e: any) => {
      const payload = JSON.parse(e.data);
      setActiveStepIndex(5);
      setCreatedIncidentId(payload.incident_id);
      setLiveLog(prev => [{ stage: 'Incident Created', data: payload, time: new Date() }, ...prev]);
      fetchRuns();
    });

    return () => {
      eventSource.close();
    };
  }, []);

  const handleRunUrl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pasteUrl) return;
    setIsProcessing(true);
    setCreatedIncidentId(null);
    try {
      await api.triggerIngestion({
        corridor,
        mode: 'url',
        url: pasteUrl
      });
      fetchRuns();
    } catch (err: any) {
      alert(`Ingestion error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRunSearch = async () => {
    setIsProcessing(true);
    setCreatedIncidentId(null);
    try {
      await api.triggerIngestion({
        corridor,
        mode: 'search'
      });
      fetchRuns();
    } catch (err: any) {
      alert(`Ingestion error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-ridge-deep via-ridge-navy to-ridge-deep p-6 rounded-2xl border border-ridge-darkborder shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">
              Web Intelligence Engine
            </span>
            <span className="text-gray-400 text-xs">Zero Manual Scrapers</span>
          </div>
          <h1 className="text-2xl font-black text-white tracking-wide">
            TinyFish Live Autonomous Pipeline
          </h1>
          <p className="text-xs text-gray-300 max-w-2xl mt-1 leading-relaxed">
            Continuously monitors regional news, state police bulletins, and emergency disaster advisories across India's North-Eastern Region. Cleanly parses unstructured prose into validated geospatial incidents with cryptographic provenance.
          </p>
        </div>

        {/* TinyFish Attribution Link */}
        <div className="flex flex-col items-end gap-2">
          <a
            href="https://docs.tinyfish.ai"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-ridge-darkcard border border-ridge-darkborder text-xs text-gray-300 hover:text-white hover:border-orange-500/50 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-orange-400" />
            <span>Powered by <strong>TinyFish API</strong></span>
            <ExternalLink className="w-3 h-3 ml-1" />
          </a>
          <button
            onClick={handleRunSearch}
            disabled={isProcessing}
            className="px-4 py-2 bg-ridge-orange hover:bg-orange-600 text-white font-bold text-xs rounded-xl shadow-lg transition-all flex items-center gap-2 disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${isProcessing ? 'animate-spin' : ''}`} />
            <span>{isProcessing ? 'Executing Run...' : `Discover New ${corridor} Advisories`}</span>
          </button>
        </div>
      </div>

      {/* Paste URL Box (The Demo Winner) */}
      <div className="bg-ridge-darkcard border border-ridge-darkborder rounded-2xl p-5 shadow-lg">
        <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
          <LinkIcon className="w-4 h-4 text-orange-400" />
          Live Advisory Ingestion: Paste Public Advisory URL
        </h2>
        <p className="text-xs text-gray-400 mb-3">
          Paste any live government advisory, local news bulletin or disaster blog URL to see TinyFish fetch and convert it live into a geo-referenced incident.
        </p>
        <form onSubmit={handleRunUrl} className="flex gap-2">
          <input
            type="url"
            value={pasteUrl}
            onChange={(e) => setPasteUrl(e.target.value)}
            placeholder="e.g. https://sikkimexpress.com/news/nh10-massive-landslide-at-29th-mile-traffic-halted"
            className="flex-1 bg-ridge-deep border border-ridge-darkborder rounded-xl px-4 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-ridge-orange"
            required
          />
          <button
            type="submit"
            disabled={isProcessing}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl shadow-md transition-all disabled:opacity-50 flex items-center gap-2"
          >
            <span>{isProcessing ? 'Fetching with TinyFish...' : 'Process URL Live'}</span>
          </button>
        </form>

        {createdIncidentId && (
          <div className="mt-3 p-3 bg-emerald-950/40 border border-emerald-500/40 rounded-xl flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-emerald-300 font-medium">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Incident created successfully with complete provenance and confidence metrics!</span>
            </div>
            <button
              onClick={onNavigateToMap}
              className="text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 px-3 py-1.5 rounded-lg shadow-sm"
            >
              Show Reroute on Map →
            </button>
          </div>
        )}
      </div>

      {/* Visual Stepper */}
      <div className="bg-ridge-darkcard border border-ridge-darkborder rounded-2xl p-6 shadow-lg">
        <h3 className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-4">
          Pipeline Execution Stepper (Real-time SSE Stream)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {steps.map((st, idx) => {
            const Icon = st.icon;
            const isCompleted = activeStepIndex > idx;
            const isCurrent = activeStepIndex === idx;

            return (
              <div
                key={st.id}
                className={`p-4 rounded-xl border transition-all ${
                  isCurrent
                    ? 'bg-ridge-deep border-ridge-orange shadow-lg shadow-orange-500/10 ring-1 ring-orange-500'
                    : isCompleted
                    ? 'bg-emerald-950/20 border-emerald-500/40'
                    : 'bg-ridge-deep/40 border-ridge-darkborder opacity-60'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className={`p-2 rounded-lg ${
                    isCurrent ? 'bg-orange-500 text-white' : isCompleted ? 'bg-emerald-500 text-white' : 'bg-gray-800 text-gray-400'
                  }`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  {isCompleted && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                  {isCurrent && <span className="w-2 h-2 rounded-full bg-orange-400 animate-ping"></span>}
                </div>
                <h4 className="text-xs font-bold text-white mb-1">{st.name}</h4>
                <p className="text-[11px] text-gray-400">{st.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Live SSE Feed & Recent Runs Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left: SSE Stream Output */}
        <div className="bg-ridge-darkcard border border-ridge-darkborder rounded-2xl p-4 shadow-lg flex flex-col h-80">
          <div className="flex items-center justify-between border-b border-ridge-darkborder pb-2.5 mb-2.5">
            <h3 className="text-xs font-bold text-white flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Live Pipeline Stream Output
            </h3>
            <span className="text-[10px] text-gray-400">SSE /api/stream/pipeline</span>
          </div>
          <div className="flex-1 overflow-y-auto space-y-2 pr-1 font-mono text-[11px]">
            {liveLog.length === 0 ? (
              <div className="text-gray-500 text-center py-16">
                Waiting for pipeline events... Trigger a run or paste an advisory URL above.
              </div>
            ) : (
              liveLog.map((log, idx) => (
                <div key={idx} className="p-2 rounded bg-black/40 border border-gray-800">
                  <div className="flex justify-between text-orange-400 font-bold mb-1">
                    <span>[{log.stage}]</span>
                    <span className="text-gray-500">{new Date(log.time).toLocaleTimeString()}</span>
                  </div>
                  <pre className="text-gray-300 text-[10px] overflow-x-auto whitespace-pre-wrap">
                    {JSON.stringify(log.data, null, 2)}
                  </pre>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right: Ingestion History Table */}
        <div className="bg-ridge-darkcard border border-ridge-darkborder rounded-2xl p-4 shadow-lg flex flex-col h-80">
          <div className="flex items-center justify-between border-b border-ridge-darkborder pb-2.5 mb-2.5">
            <h3 className="text-xs font-bold text-white">Recent Ingestion Runs</h3>
            <span className="text-[10px] text-gray-400">Last 10 executions</span>
          </div>
          <div className="flex-1 overflow-y-auto">
            <table className="w-full text-left text-xs text-gray-300">
              <thead className="text-[10px] uppercase text-gray-400 bg-ridge-deep/60 border-b border-ridge-darkborder">
                <tr>
                  <th className="p-2">Corridor</th>
                  <th className="p-2">Mode</th>
                  <th className="p-2">API Used</th>
                  <th className="p-2">Incidents</th>
                  <th className="p-2">Duration</th>
                  <th className="p-2">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ridge-darkborder">
                {recentRuns.map((r) => (
                  <tr key={r.id} className="hover:bg-white/5 transition-colors">
                    <td className="p-2 font-medium text-white">{r.corridor}</td>
                    <td className="p-2 uppercase text-[10px]">{r.mode}</td>
                    <td className="p-2 text-gray-400 text-[11px]">{r.tinyfish_api_used}</td>
                    <td className="p-2 text-emerald-400 font-bold">+{r.new_incidents_count}</td>
                    <td className="p-2 text-gray-400">{r.duration_ms}ms</td>
                    <td className="p-2">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-500/30">
                        {r.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
