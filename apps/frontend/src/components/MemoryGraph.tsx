"use client";

import { useEffect, useState, useRef } from "react";
import { Loader2, Network, ZoomIn, ZoomOut, RotateCcw } from "lucide-react";

interface Node {
  id: string;
  label: string;
  type: string;
  val: number;
  x?: number;
  y?: number;
}

interface Edge {
  source: string;
  target: string;
  label: string;
}

interface MemoryGraphProps {
  entity: string;
}

export default function MemoryGraph({ entity }: MemoryGraphProps) {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [containerSize, setContainerSize] = useState<{ width: number; height: number }>({ width: 500, height: 400 });
  const containerRef = useRef<HTMLDivElement>(null);
  const isDraggingRef = useRef<boolean>(false);
  const dragStartRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  // Track container size for centering the graph (ref reads are unsafe during render)
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const observer = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect;
      setContainerSize({ width, height });
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!entity) return;

    const fetchGraphData = async () => {
      setLoading(true);
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${baseUrl}/api/memory/${encodeURIComponent(entity)}`);
        if (res.ok) {
          const data = await res.json();
          
          // Generate organic positions for nodes
          const processedNodes = data.nodes.map((node: Node, index: number) => {
            const angle = (index / data.nodes.length) * 2 * Math.PI;
            const radius = index === 0 ? 0 : 120 + Math.random() * 40;
            return {
              ...node,
              x: radius * Math.cos(angle),
              y: radius * Math.sin(angle)
            };
          });
          
          setNodes(processedNodes);
          setEdges(data.edges);
          if (processedNodes.length > 0) {
            setSelectedNode(processedNodes[0]);
          }
        }
      } catch (err) {
        console.error("Failed to load memory graph nodes:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchGraphData();
  }, [entity]);

  // Handle Mouse Drag / Pan operations
  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).tagName === "circle") return; // Let clicks on nodes pass through
    isDraggingRef.current = true;
    dragStartRef.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDraggingRef.current) return;
    setPan({
      x: e.clientX - dragStartRef.current.x,
      y: e.clientY - dragStartRef.current.y
    });
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  const getNodeColor = (type: string) => {
    switch (type?.toUpperCase()) {
      case "COMPANY":
        return "#00D4FF"; // Cyber Cyan
      case "PERSON":
        return "#FF6B35"; // Alert Amber
      case "VULNERABILITY":
      case "THREAT":
        return "#EF4444"; // Alarm Red
      case "PRODUCT":
      case "DOMAIN":
        return "#00FF88"; // Success Emerald
      default:
        return "#A855F7"; // Cool Purple
    }
  };

  return (
    <div 
      className="relative flex flex-col h-full w-full bg-slate-950/20 backdrop-blur-md rounded-xl border border-white/10 overflow-hidden select-none"
      ref={containerRef}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {/* Visual Header */}
      <div className="absolute top-4 left-4 z-10 flex items-center space-x-2">
        <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
          <Network className="w-4 h-4 text-cyan-400 animate-pulse" />
        </div>
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-white font-mono uppercase">Memory Knowledge Graph</h3>
          <p className="text-xs text-white/40">Cognee persistent entity relationships</p>
        </div>
      </div>

      {/* Control Widgets */}
      <div className="absolute bottom-4 right-4 z-10 flex items-center bg-black/60 border border-white/10 rounded-lg p-1.5 space-x-2">
        <button 
          onClick={() => setZoom(prev => Math.min(prev + 0.15, 2.5))}
          className="p-1 text-white/60 hover:text-cyan-400 transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-3.5 h-3.5" />
        </button>
        <button 
          onClick={() => setZoom(prev => Math.max(prev - 0.15, 0.4))}
          className="p-1 text-white/60 hover:text-cyan-400 transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-3.5 h-3.5" />
        </button>
        <button 
          onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}
          className="p-1 text-white/60 hover:text-cyan-400 transition-colors"
          title="Reset View"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-slate-950/75 z-20 flex flex-col items-center justify-center space-y-2">
          <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
          <span className="text-xs text-cyan-300 font-mono">Reconstructing semantic memories...</span>
        </div>
      )}

      {/* Render Node Details Sidebar overlay */}
      {selectedNode && (
        <div className="absolute top-16 left-4 z-10 w-64 bg-black/70 backdrop-blur-lg border border-white/10 p-3 rounded-lg flex flex-col space-y-1.5">
          <div className="flex items-center justify-between border-b border-white/10 pb-1.5">
            <span className="text-xs text-white/40 font-mono tracking-wider">ENTITY DESCRIPTOR</span>
            <span 
              className="text-[9px] px-1.5 py-0.5 rounded font-mono font-bold" 
              style={{ 
                backgroundColor: `${getNodeColor(selectedNode.type)}20`,
                color: getNodeColor(selectedNode.type),
                border: `1px solid ${getNodeColor(selectedNode.type)}40`
              }}
            >
              {selectedNode.type}
            </span>
          </div>
          <div>
            <h4 className="text-sm font-bold text-white font-mono">{selectedNode.label}</h4>
            <p className="text-xs text-white/50 mt-1">
              {selectedNode.type === "COMPANY" 
                ? "Autonomous threat monitor targets, GTM scaling parameters, and product interfaces."
                : selectedNode.type === "VULNERABILITY" 
                ? "Severe credential leakage threat vector mapped in public subcontractor code repositories."
                : "Monitored executive personnel representing corporate operations."
              }
            </p>
          </div>
          <div className="flex items-center space-x-2 pt-1">
            <div className="flex-1 text-[10px] bg-white/5 p-1 rounded font-mono text-white/70">
              ID: <span className="text-white/40">{selectedNode.id.substring(0, 8)}...</span>
            </div>
            <div className="text-[10px] bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 p-1 rounded font-mono">
              Weight: {selectedNode.val}
            </div>
          </div>
        </div>
      )}

      {/* Central Interactive SVG Canvas */}
      <svg 
        className="flex-1 w-full h-full cursor-grab active:cursor-grabbing"
        style={{ background: "radial-gradient(circle at center, #0B0E14 0%, #050608 100%)" }}
      >
        <defs>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>
        
        {/* Dynamic Transformed Group based on pan & zoom */}
        <g transform={`translate(${pan.x + containerSize.width / 2}, ${pan.y + containerSize.height / 2}) scale(${zoom})`}>
          
          {/* Render Connections (Edges) */}
          {edges.map((edge, idx) => {
            const sourceNode = nodes.find(n => n.id === edge.source);
            const targetNode = nodes.find(n => n.id === edge.target);
            
            if (!sourceNode || !targetNode) return null;
            
            return (
              <g key={`edge-${idx}`}>
                <line
                  x1={sourceNode.x}
                  y1={sourceNode.y}
                  x2={targetNode.x}
                  y2={targetNode.y}
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="1.5"
                  strokeDasharray={edge.label === "associated" ? "0" : "4 4"}
                />
              </g>
            );
          })}

          {/* Render Entity Nodes */}
          {nodes.map((node) => {
            const isSelected = selectedNode?.id === node.id;
            const color = getNodeColor(node.type);
            
            return (
              <g 
                key={node.id} 
                transform={`translate(${node.x}, ${node.y})`}
                onClick={() => setSelectedNode(node)}
                className="group cursor-pointer"
              >
                {/* Outer Glow on hover/selection */}
                <circle
                  r={isSelected ? node.val * 1.5 + 4 : node.val + 2}
                  fill="none"
                  stroke={color}
                  strokeWidth={isSelected ? 2 : 1}
                  className="transition-all duration-300 opacity-30 group-hover:opacity-60"
                  filter={isSelected ? "url(#glow)" : undefined}
                />
                
                {/* Main Node Circle */}
                <circle
                  r={node.val}
                  fill={color}
                  className="transition-all duration-300"
                  style={{ fillOpacity: isSelected ? 0.95 : 0.7 }}
                />

                {/* Inner Core Accent */}
                <circle
                  r={node.val * 0.3}
                  fill="#ffffff"
                  className="opacity-70"
                />

                {/* Node Label text */}
                <text
                  y={node.val + 14}
                  textAnchor="middle"
                  className="text-[10px] fill-white/80 font-mono tracking-wide pointer-events-none select-none transition-all duration-300 group-hover:fill-cyan-400"
                >
                  {node.label}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
}
