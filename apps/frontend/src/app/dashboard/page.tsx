"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import {
  Shield, Terminal, Activity, Play,
  Download, AlertTriangle, CheckCircle, RefreshCw, Clock, Globe, FileText
} from "lucide-react";
import { useInvestigation } from "@/hooks/useInvestigation";
import MemoryGraph from "@/components/MemoryGraph";

interface PastInvestigation {
  id: string;
  target: string;
  risk_score: number;
  created_at: string;
}

interface WorkflowEvent {
  event_type: string;
  triggered_at: string;
}

export default function DashboardPage() {
  const { investigate, steps, report, loading, error, activeTarget } = useInvestigation();
  const [targetInput, setTargetInput] = useState<string>("OpenAI");
  const [selectedFocus, setSelectedFocus] = useState<string[]>(["security", "hiring", "pricing"]);
  const [pastInvestigations, setPastInvestigations] = useState<PastInvestigation[]>([]);
  const [workflowsTriggered, setWorkflowsTriggered] = useState<WorkflowEvent[]>([]);

  const terminalEndRef = useRef<HTMLDivElement>(null);
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Fetch past logs on load
  const fetchLogs = useCallback(async () => {
    try {
      const invsRes = await fetch(`${baseUrl}/api/investigations`);
      if (invsRes.ok) {
        const data = await invsRes.json();
        setPastInvestigations(data);
      }

      const wfRes = await fetch(`${baseUrl}/api/workflows`);
      if (wfRes.ok) {
        const data = await wfRes.json();
        setWorkflowsTriggered(data);
      }
    } catch (err) {
      console.error("Failed to load historical database logs:", err);
    }
  }, [baseUrl]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- intentional refetch of history whenever a scan completes
    fetchLogs();
  }, [report, fetchLogs]); // Refresh logs every time a scan completes successfully!

  // Auto-scroll terminal logs
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [steps]);

  const handleFocusToggle = (focus: string) => {
    setSelectedFocus(prev => 
      prev.includes(focus) ? prev.filter(f => f !== focus) : [...prev, focus]
    );
  };

  const handleLaunch = () => {
    if (!targetInput.trim() || loading) return;
    investigate(targetInput.trim(), selectedFocus);
  };

  // Export report to markdown
  const handleExport = async (id: string) => {
    try {
      const res = await fetch(`${baseUrl}/api/report/${id}/export`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        const blob = new Blob([data.markdown], { type: "text/markdown" });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = data.filename;
        link.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error("Failed to export report markdown:", err);
      alert("Failed to export report markdown.");
    }
  };

  // Compute Risk Level Color Class
  const getRiskColor = (score: number) => {
    if (score >= 8.0) return "text-red-500 border-red-500 bg-red-500/10";
    if (score >= 6.0) return "text-orange-500 border-orange-500 bg-orange-500/10";
    if (score >= 4.0) return "text-yellow-500 border-yellow-500 bg-yellow-500/10";
    return "text-emerald-500 border-emerald-500 bg-emerald-500/10";
  };

  return (
    <div className="relative min-h-screen flex flex-col bg-[#050508] cyber-grid-light select-none text-slate-200">
      
      {/* Background radial effects */}
      <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-500/3 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-orange-500/2 blur-[120px] pointer-events-none" />

      {/* Global Dashboard Navigation Bar */}
      <header className="relative z-10 w-full px-6 py-4 flex items-center justify-between border-b border-white/5 bg-slate-950/40 backdrop-blur-md">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
            <Shield className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-md font-bold tracking-widest text-white font-mono flex items-center">
              AEGIS <span className="text-xs text-cyan-400 font-normal ml-2 font-sans tracking-normal bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">OPERATIONAL CONSOLE</span>
            </h1>
            <p className="text-[10px] text-white/40 font-mono">Autonomous Enterprise Intelligence OS v1.0.0</p>
          </div>
        </div>

        {/* Input Target Deck */}
        <div className="flex items-center space-x-4 bg-black/40 border border-white/10 rounded-lg p-1.5 max-w-2xl w-full mx-4">
          <div className="flex items-center space-x-2 flex-1 pl-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <input 
              type="text" 
              placeholder="Enter Target Company (e.g. OpenAI, Anthropic)" 
              value={targetInput}
              onChange={(e) => setTargetInput(e.target.value)}
              className="w-full bg-transparent border-none text-sm text-white focus:outline-none focus:ring-0 font-mono"
              disabled={loading}
            />
          </div>
          
          {/* Checkboxes focus */}
          <div className="hidden lg:flex items-center space-x-3 border-l border-white/10 px-3">
            {[
              { id: "security", label: "Security Risk" },
              { id: "hiring", label: "Hiring Signal" },
              { id: "pricing", label: "Pricing Shift" }
            ].map((f) => (
              <label key={f.id} className="flex items-center space-x-1.5 cursor-pointer select-none">
                <input 
                  type="checkbox"
                  checked={selectedFocus.includes(f.id)}
                  onChange={() => handleFocusToggle(f.id)}
                  className="rounded bg-black border-white/20 text-cyan-500 focus:ring-0 w-3 h-3 cursor-pointer"
                  disabled={loading}
                />
                <span className="text-[10px] text-white/60 font-mono hover:text-white transition-colors">{f.label}</span>
              </label>
            ))}
          </div>

          <button 
            onClick={handleLaunch}
            disabled={loading || !targetInput.trim()}
            className="flex items-center space-x-1.5 bg-cyan-500 hover:bg-cyan-600 disabled:bg-slate-800 disabled:text-white/40 text-black px-4 py-2 rounded font-mono font-bold text-xs tracking-wider transition-colors shadow-lg shadow-cyan-500/10 cursor-pointer"
          >
            {loading ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>INVESTIGATING...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-black" />
                <span>INVESTIGATE</span>
              </>
            )}
          </button>
        </div>

        <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
          <Activity className="w-3.5 h-3.5 animate-pulse" />
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider">RADAR SCANNING</span>
        </div>
      </header>

      {/* Connection / pipeline error banner */}
      {error && (
        <div className="relative z-10 mx-4 mt-4 flex items-center space-x-2 px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span className="text-xs font-mono">{error}</span>
        </div>
      )}

      {/* Main Command Dashboard Layout */}
      <div className="flex-1 grid grid-cols-1 xl:grid-cols-4 gap-4 p-4">
        
        {/* LEFT COLUMN: LIVE SIGNAL RADAR (Severity logs) */}
        <div className="xl:col-span-1 flex flex-col space-y-4 h-[calc(100vh-100px)] overflow-hidden">
          
          <div className="glass-card flex-1 rounded-xl p-4 flex flex-col overflow-hidden border border-white/5">
            <div className="flex items-center justify-between border-b border-white/5 pb-3 mb-3">
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-orange-400" />
                <h2 className="text-xs font-bold tracking-widest font-mono text-white uppercase">Live Threat Beacons</h2>
              </div>
              <span className="text-[9px] bg-orange-500/10 text-orange-400 border border-orange-500/20 px-2 py-0.5 rounded font-mono">
                REALTIME
              </span>
            </div>

            {/* SSE Dynamic signal dispatches */}
            <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
              {steps.filter(s => s.type === "signal").length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center text-white/30 space-y-1.5">
                  <Activity className="w-8 h-8 opacity-20" />
                  <p className="text-[10px] font-mono">No telemetry beacons detected in active queue.</p>
                </div>
              ) : (
                steps.filter(s => s.type === "signal").map((sig, i) => (
                  <div 
                    key={i} 
                    className="p-3 rounded-lg border bg-black/40 border-white/5 transition-all duration-300 hover:border-white/10 flex flex-col space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded font-mono font-bold tracking-wider">
                        {sig.signal}
                      </span>
                      <span className="text-[9px] text-white/40 font-mono">
                        {sig.timestamp ? new Date(sig.timestamp).toLocaleTimeString() : ""}
                      </span>
                    </div>
                    <p className="text-xs text-white font-medium">{sig.entity}</p>
                    <p className="text-[10px] text-white/60 leading-relaxed font-sans">{sig.detail}</p>
                    <div className="flex items-center justify-between pt-1 text-[9px] border-t border-white/5">
                      <span className="text-white/40">Severity</span>
                      <span className="text-red-400 font-bold font-mono">{sig.severity}/10</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
          
          {/* Active Workflows logs widget */}
          <div className="glass-card h-[250px] rounded-xl p-4 flex flex-col overflow-hidden border border-white/5 bg-black/25">
            <div className="flex items-center justify-between border-b border-white/5 pb-2 mb-2">
              <div className="flex items-center space-x-2">
                <Globe className="w-4 h-4 text-emerald-400" />
                <h2 className="text-xs font-bold tracking-widest font-mono text-white uppercase">TriggerWare dispatches</h2>
              </div>
              <span className="w-2 h-2 rounded-full bg-emerald-400 blink-dot" />
            </div>
            
            <div className="flex-1 overflow-y-auto space-y-2">
              {workflowsTriggered.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center text-white/20 text-[10px] font-mono">
                  No automated dispatches logged.
                </div>
              ) : (
                workflowsTriggered.map((wf, idx) => (
                  <div key={idx} className="p-2 rounded bg-black/40 border border-white/5 flex items-center justify-between text-[10px]">
                    <div className="flex flex-col">
                      <span className="font-bold font-mono text-cyan-400">{wf.event_type}</span>
                      <span className="text-white/40 text-[9px]">{new Date(wf.triggered_at).toLocaleString()}</span>
                    </div>
                    <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      DELIVERED
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* CENTER COLUMN (XL COGNITION STREAM TERMINAL & Memory Graph) */}
        <div className="xl:col-span-2 flex flex-col space-y-4 h-[calc(100vh-100px)] overflow-hidden">
          
          {/* Terminal stream panel */}
          <div className="glass-card flex-1 rounded-xl p-4 flex flex-col overflow-hidden border border-white/5 relative">
            
            <div className="flex items-center justify-between border-b border-white/5 pb-3 mb-3">
              <div className="flex items-center space-x-2">
                <Terminal className="w-4 h-4 text-cyan-400" />
                <h2 className="text-xs font-bold tracking-widest font-mono text-white uppercase">Cognitive Reasoning Stream</h2>
              </div>
              
              <div className="flex items-center space-x-2 text-[9px] font-mono text-white/40">
                <Clock className="w-3 h-3 text-cyan-400" />
                <span>SCAN: {activeTarget || "IDLE"}</span>
              </div>
            </div>

            {/* Hacker log scrolling block */}
            <div className="flex-1 overflow-y-auto bg-black/70 rounded-lg p-3 border border-white/5 font-mono text-xs leading-relaxed space-y-1.5 select-text">
              {steps.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-white/30 space-y-1">
                  <span className="text-cyan-400/20 text-4xl font-extralight select-none">$</span>
                  <p className="text-[10px] uppercase tracking-wider text-white/20 select-none">SYSTEM INACTIVE. ENTER A TARGET AND INITIATE AEGIS INTELLIGENCE PATROL.</p>
                </div>
              ) : (
                steps.map((step, idx) => {
                  if (step.type === "step") {
                    let prefix = "[INFO]";
                    let color = "text-white/60";
                    
                    if (step.step === "scout") { prefix = "[SCOUT]"; color = "text-cyan-400"; }
                    if (step.step === "investigate") { prefix = "[INVESTIGATE]"; color = "text-amber-400"; }
                    if (step.step === "synthesize") { prefix = "[SYNTHESIZE]"; color = "text-purple-400"; }
                    if (step.step === "error") { prefix = "[CRITICAL]"; color = "text-red-500 font-bold"; }
                    
                    return (
                      <div key={idx} className={`${color} flex items-start space-x-2`}>
                        <span className="opacity-50">[{new Date(step.timestamp).toLocaleTimeString()}]</span>
                        <span className="font-bold">{prefix}</span>
                        <span className="flex-1">{step.message}</span>
                      </div>
                    );
                  }
                  return null;
                })
              )}
              {loading && (
                <div className="flex items-center space-x-2 text-cyan-400 font-bold animate-pulse">
                  <span>&gt;</span>
                  <span className="blink-dot">_</span>
                  <span>Agent executing neural graph pathways...</span>
                </div>
              )}
              <div ref={terminalEndRef} />
            </div>
          </div>

          {/* Bottom D3 Memory Graph panel */}
          <div className="h-[350px] w-full">
            <MemoryGraph entity={activeTarget || (pastInvestigations[0]?.target || "OpenAI")} />
          </div>
        </div>

        {/* RIGHT COLUMN: INTELLIGENCE EXECUTIVE REPORT & PAST RUNS */}
        <div className="xl:col-span-1 flex flex-col space-y-4 h-[calc(100vh-100px)] overflow-hidden">
          
          {/* Executive report card */}
          <div className="glass-card flex-1 rounded-xl p-4 flex flex-col overflow-hidden border border-white/5 bg-black/10">
            
            <div className="flex items-center justify-between border-b border-white/5 pb-2 mb-2">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-cyan-400" />
                <h2 className="text-xs font-bold tracking-widest font-mono text-white uppercase">Executive Briefing</h2>
              </div>
              
              {report && (
                <button 
                  onClick={() => handleExport(pastInvestigations[0]?.id || "export")}
                  className="p-1 rounded bg-white/5 hover:bg-white/10 text-white/70 hover:text-cyan-400 border border-white/10 transition-all cursor-pointer"
                  title="Export Markdown"
                >
                  <Download className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Report Viewer */}
            <div className="flex-1 overflow-y-auto space-y-4 pr-1">
              {!report ? (
                <div className="h-full flex flex-col items-center justify-center text-center text-white/30 space-y-1.5">
                  <FileText className="w-8 h-8 opacity-20" />
                  <p className="text-[10px] font-mono">Run scan target to compile structured executive report.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  
                  {/* Glowing Threat Gauge */}
                  <div className="flex items-center space-x-3 bg-black/60 p-3 rounded-lg border border-white/5">
                    <div className={`p-2.5 rounded-lg border font-mono font-bold text-center text-sm w-14 h-14 flex flex-col items-center justify-center ${getRiskColor(report.risk_score)}`}>
                      <span className="text-[8px] opacity-40 leading-none">THREAT</span>
                      <span className="text-base font-black mt-0.5">{report.risk_score.toFixed(1)}</span>
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-mono text-white/40 tracking-wider">RISK CLASSIFICATION</span>
                        <span className="text-[10px] font-bold text-cyan-400 tracking-widest">{report.risk_level}</span>
                      </div>
                      <p className="text-[11px] text-white/60 font-sans mt-0.5 truncate">
                        Autonomous dispatches: {report.workflows_triggered.join(", ") || "None"}
                      </p>
                    </div>
                  </div>

                  {/* Summary Block */}
                  <div className="space-y-1.5">
                    <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest block">Executive Summary</span>
                    <p className="text-xs text-white/80 leading-relaxed font-sans bg-black/35 p-3 rounded border border-white/5">{report.executive_summary}</p>
                  </div>

                  {/* Recommendations */}
                  <div className="space-y-2">
                    <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest block">Response Directives</span>
                    <div className="space-y-1.5">
                      {report.recommendations.map((rec, i) => (
                        <div key={i} className="flex items-start space-x-2 text-xs bg-slate-900/40 p-2.5 rounded border border-white/5">
                          <CheckCircle className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                          <span className="text-white/80">{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* References & Links */}
                  <div className="space-y-2">
                    <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest block">Scrape References</span>
                    <div className="space-y-1.5">
                      {report.sources.map((src, i) => (
                        <a 
                          key={i} 
                          href={src.url} 
                          target="_blank" 
                          rel="noreferrer"
                          className="flex items-center justify-between p-2 rounded bg-black/40 border border-white/5 text-xs text-white/60 hover:text-cyan-400 hover:border-cyan-500/20 transition-all"
                        >
                          <span className="truncate max-w-[150px] font-mono text-[10px]">{src.title}</span>
                          <Globe className="w-3 h-3 text-white/40 shrink-0 ml-2" />
                        </a>
                      ))}
                    </div>
                  </div>

                  {/* Cognee Memory block */}
                  <div className="space-y-1.5">
                    <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest block">Graph Memory Context</span>
                    <p className="text-[10px] text-white/60 leading-relaxed font-mono bg-black/40 p-2.5 rounded border border-white/5 whitespace-pre-line">
                      {report.prior_context}
                    </p>
                  </div>

                </div>
              )}
            </div>
          </div>

          {/* Past investigations history widget */}
          <div className="glass-card h-[250px] rounded-xl p-4 flex flex-col overflow-hidden border border-white/5 bg-black/25">
            <div className="flex items-center justify-between border-b border-white/5 pb-2 mb-2">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-cyan-400" />
                <h2 className="text-xs font-bold tracking-widest font-mono text-white uppercase">Historical Scans</h2>
              </div>
              <span className="text-[9px] text-white/40 font-mono">DB LOG</span>
            </div>

            <div className="flex-1 overflow-y-auto space-y-2">
              {pastInvestigations.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center text-white/20 text-[10px] font-mono">
                  No historical scans registered.
                </div>
              ) : (
                pastInvestigations.map((inv, idx) => (
                  <div 
                    key={idx} 
                    className="p-2 rounded bg-black/40 border border-white/5 flex items-center justify-between cursor-pointer hover:border-cyan-500/30 transition-all"
                  >
                    <div className="flex flex-col min-w-0">
                      <span className="font-bold text-white font-mono text-[10px] truncate">{inv.target}</span>
                      <span className="text-white/40 text-[9px]">{new Date(inv.created_at).toLocaleDateString()}</span>
                    </div>
                    
                    <div className="flex items-center space-x-2 shrink-0">
                      <span className={`text-[9px] font-mono px-1 rounded ${getRiskColor(inv.risk_score)}`}>
                        {inv.risk_score.toFixed(1)}
                      </span>
                      <button
                        onClick={() => handleExport(inv.id)}
                        className="p-1 rounded bg-white/5 hover:bg-cyan-500/10 text-white/50 hover:text-cyan-400 cursor-pointer"
                        title="Download report markdown"
                      >
                        <Download className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
