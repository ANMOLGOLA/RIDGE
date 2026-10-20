import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  ExternalLink, 
  ShieldAlert, 
  AlertTriangle, 
  Clock, 
  FileText,
  UserCheck
} from 'lucide-react';
import { Incident, api } from '../lib/api';

interface VerificationQueuePageProps {
  corridor: string;
}

export const VerificationQueuePage: React.FC<VerificationQueuePageProps> = ({ corridor }) => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [verificationNote, setVerificationNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchQueue = async () => {
    try {
      // Fetch incidents with low/medium confidence (<0.85) or status pending
      const list = await api.getIncidents({ corridor });
      // Filter for unverified or low confidence items
      const unverified = list.filter(i => !i.verified_by || i.confidence < 0.80);
      setIncidents(unverified);
      if (unverified.length > 0 && !selectedIncident) {
        setSelectedIncident(unverified[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, [corridor]);

  const handleDecision = async (decision: 'confirm' | 'reject') => {
    if (!selectedIncident) return;
    setIsSubmitting(true);
    try {
      const updated = await api.verifyIncident(selectedIncident.id, {
        decision,
        note: verificationNote || (decision === 'confirm' ? 'Verified by disaster duty officer' : 'False positive / road operational'),
        verifier: 'State Disaster Management Officer'
      });
      alert(`Incident ${decision === 'confirm' ? 'CONFIRMED' : 'REJECTED'}. Risk scores updated!`);
      setVerificationNote('');
      fetchQueue();
      setSelectedIncident(null);
    } catch (err: any) {
      alert(`Verification error: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4 max-w-7xl mx-auto pb-12">
      {/* Page Title */}
      <div className="bg-ridge-darkcard border border-ridge-darkborder p-5 rounded-2xl flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-orange-400" />
            <h1 className="text-xl font-bold text-white">Authority Verification Queue</h1>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Incidents with intelligence confidence &lt; 0.80 require official human confirmation before long-haul logistics fleets are rerouted.
          </p>
        </div>
        <span className="px-3 py-1 bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-xl text-xs font-bold">
          {incidents.length} Pending Review
        </span>
      </div>

      {incidents.length === 0 ? (
        <div className="bg-ridge-darkcard border border-ridge-darkborder rounded-2xl p-16 text-center">
          <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
          <h2 className="text-base font-bold text-white">All Clear! Queue is Empty</h2>
          <p className="text-xs text-gray-400 max-w-md mx-auto mt-1">
            All reports on {corridor} meet the 80%+ confidence threshold or have already been reviewed by an authority officer.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Left Column: List of items (5 cols) */}
          <div className="lg:col-span-5 space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {incidents.map((inc) => {
              const isSelected = selectedIncident?.id === inc.id;
              return (
                <div
                  key={inc.id}
                  onClick={() => setSelectedIncident(inc)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-ridge-deep border-ridge-orange shadow-lg ring-1 ring-orange-500'
                      : 'bg-ridge-darkcard border-ridge-darkborder hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center justify-between gap-1 mb-1.5">
                    <span className="font-bold text-xs text-white line-clamp-1">
                      {inc.title}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950 text-amber-300 border border-amber-500/30">
                      Conf: {Math.round(inc.confidence * 100)}%
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-400 line-clamp-2 mb-2">
                    {inc.summary}
                  </p>
                  <div className="flex items-center justify-between text-[10px] text-gray-500 pt-1.5 border-t border-gray-800">
                    <span>{inc.location_text}</span>
                    <span>{new Date(inc.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right Column: Detailed Review & Confirm/Reject (7 cols) */}
          {selectedIncident && (
            <div className="lg:col-span-7 bg-ridge-darkcard border border-ridge-darkborder rounded-2xl p-5 shadow-xl space-y-4">
              <div className="border-b border-ridge-darkborder pb-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-orange-400">
                    Incident ID: {selectedIncident.id}
                  </span>
                  <span className="text-xs text-gray-400">
                    Source: <strong>{selectedIncident.provenance.domain || 'Regional Bulletin'}</strong>
                  </span>
                </div>
                <h2 className="text-lg font-bold text-white">
                  {selectedIncident.title}
                </h2>
              </div>

              {/* Side by side: Extracted Data vs Source Evidence */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                {/* Extracted Attributes */}
                <div className="bg-ridge-deep p-3 rounded-xl border border-ridge-darkborder space-y-2">
                  <span className="font-bold text-gray-300 block border-b border-gray-700 pb-1">
                    Structured Attributes
                  </span>
                  <div className="space-y-1 text-gray-400">
                    <div>Road: <span className="text-white font-medium">{selectedIncident.road || corridor}</span></div>
                    <div>Location: <span className="text-white font-medium">{selectedIncident.location_text}</span></div>
                    <div>Event Type: <span className="text-white font-medium uppercase">{selectedIncident.event_type}</span></div>
                    <div>Status: <span className="text-white font-medium uppercase">{selectedIncident.status}</span></div>
                    <div>Severity: <span className="text-white font-medium">{selectedIncident.severity} / 5</span></div>
                  </div>
                </div>

                {/* Confidence Breakdown */}
                <div className="bg-ridge-deep p-3 rounded-xl border border-ridge-darkborder space-y-2">
                  <span className="font-bold text-gray-300 block border-b border-gray-700 pb-1">
                    Confidence Breakdown ({Math.round(selectedIncident.confidence * 100)}%)
                  </span>
                  <div className="space-y-1 text-gray-400">
                    <div>Source Reliability: <span className="text-emerald-400 font-bold">{Math.round((selectedIncident.confidence_breakdown.source_reliability || 0.8) * 100)}%</span></div>
                    <div>Corroboration Count: <span className="text-blue-400 font-bold">{selectedIncident.source_count} source(s)</span></div>
                    <div>Geocoding Match: <span className="text-amber-400 font-bold">{Math.round((selectedIncident.confidence_breakdown.geocoding_precision || 0.8) * 100)}%</span></div>
                  </div>
                </div>
              </div>

              {/* Exact Evidence Quote */}
              <div className="p-3 bg-black/40 rounded-xl border border-gray-700 text-xs">
                <span className="text-gray-400 font-semibold block mb-1">
                  Extracted Evidence Quote from Page:
                </span>
                <p className="text-orange-200 italic leading-relaxed">
                  "{selectedIncident.evidence_quote || selectedIncident.summary}"
                </p>
                {selectedIncident.provenance.source_url && (
                  <a
                    href={selectedIncident.provenance.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-blue-400 hover:underline mt-2 text-[11px]"
                  >
                    <span>View original publication on {selectedIncident.provenance.domain}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>

              {/* Note Input */}
              <div>
                <label className="text-xs font-medium text-gray-400 block mb-1">
                  Official Verification Note / Duty Log:
                </label>
                <input
                  type="text"
                  value={verificationNote}
                  onChange={(e) => setVerificationNote(e.target.value)}
                  placeholder="e.g. Confirmed with local Kalimpong traffic control room at 10:15 AM"
                  className="w-full bg-ridge-deep border border-ridge-darkborder rounded-xl px-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-ridge-orange"
                />
              </div>

              {/* Decision Action Buttons */}
              <div className="flex items-center gap-3 pt-2">
                <button
                  onClick={() => handleDecision('confirm')}
                  disabled={isSubmitting}
                  className="flex-1 py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Confirm Incident (Trigger Fleet Reroute)</span>
                </button>

                <button
                  onClick={() => handleDecision('reject')}
                  disabled={isSubmitting}
                  className="flex-1 py-2.5 px-4 bg-red-600 hover:bg-red-700 text-white font-bold text-xs rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Reject as False Positive</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
