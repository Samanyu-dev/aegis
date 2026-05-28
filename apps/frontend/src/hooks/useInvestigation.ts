import { useState, useEffect, useRef } from "react";

export interface StreamEvent {
  type: "step" | "signal" | "error";
  step?: "scout" | "investigate" | "synthesize" | "error";
  message?: string;
  signal?: string;
  entity?: string;
  detail?: string;
  severity?: number;
  timestamp: string;
}

export interface Report {
  target: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  executive_summary: string;
  signals: Array<{
    type: string;
    entity: string;
    detail: string;
    severity: number;
    source_url: string;
  }>;
  entities: Array<{
    name: string;
    type: string;
    mentions: number;
  }>;
  sources: Array<{
    title: string;
    url: string;
    snippet?: string;
  }>;
  recommendations: string[];
  prior_context: string;
  workflows_triggered: string[];
  generated_at: string;
}

export function useInvestigation() {
  const [steps, setSteps] = useState<StreamEvent[]>([]);
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTarget, setActiveTarget] = useState<string>("");
  
  const eventSourceRef = useRef<EventSource | null>(null);

  const cleanup = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  };

  useEffect(() => {
    return cleanup;
  }, []);

  const investigate = async (target: string, focus: string[]) => {
    if (!target) return;
    
    // Clear previous state
    cleanup();
    setSteps([]);
    setReport(null);
    setError(null);
    setLoading(true);
    setActiveTarget(target);

    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const focusParam = focus.join(",");
    const url = `${baseUrl}/api/investigate?target=${encodeURIComponent(target)}&focus=${encodeURIComponent(focusParam)}`;

    try {
      const es = new EventSource(url);
      eventSourceRef.current = es;

      es.onmessage = (e) => {
        try {
          const event = JSON.parse(e.data);
          
          if (event.type === "step" || event.type === "signal") {
            setSteps((prev) => [...prev, event]);
          }
          
          if (event.type === "complete") {
            setReport(event.report);
            setLoading(false);
            es.close();
          }
          
          if (event.step === "error" || event.type === "error") {
            setError(event.message || "An unexpected error occurred in multi-agent pipeline.");
            setLoading(false);
            es.close();
          }
        } catch (err) {
          console.error("Failed to parse SSE event data:", err);
        }
      };

      es.onerror = (e) => {
        console.error("SSE connection error:", e);
        setError("Disconnected from AEGIS stream backend. Check server status.");
        setLoading(false);
        es.close();
      };
    } catch (err) {
      console.error("Failed to create EventSource connection:", err);
      setError(err instanceof Error ? err.message : "Failed to connect to backend engine.");
      setLoading(false);
    }
  };

  return { investigate, steps, report, loading, error, activeTarget, setSteps, setReport };
}
