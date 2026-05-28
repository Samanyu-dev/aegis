"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Shield, ArrowRight, Activity, GitBranch, Terminal } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="relative min-h-screen flex flex-col justify-between overflow-hidden bg-[#050508] cyber-grid">
      
      {/* Visual background atmospheric lights */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-cyan-500/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-500/5 blur-[120px] pointer-events-none" />

      {/* Header Bar */}
      <header className="relative z-10 w-full max-w-7xl mx-auto px-6 py-6 flex items-center justify-between border-b border-white/5">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
            <Shield className="w-6 h-6 text-cyan-400" />
          </div>
          <span className="text-xl font-bold tracking-widest text-white font-mono">AEGIS</span>
        </div>
        
        <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-slate-900/60 border border-white/5">
          <Activity className="w-3.5 h-3.5 text-emerald-400 blink-dot" />
          <span className="text-xs font-mono text-emerald-400 font-bold uppercase tracking-wider">SYSTEM ACTIVE</span>
        </div>
      </header>

      {/* Hero section */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 max-w-4xl mx-auto">
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="space-y-6"
        >
          {/* Subheading badge */}
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-mono tracking-wider uppercase mb-2">
            <Terminal className="w-3.5 h-3.5 mr-1" />
            AUTONOMOUS OS FOR INTELLIGENCE SCANNING
          </div>

          <h1 className="text-5xl md:text-7xl font-bold font-mono tracking-tight text-white leading-tight">
            The Enterprise <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-400 to-indigo-500">
              Intelligence OS
            </span>
          </h1>

          <p className="text-base md:text-lg text-slate-400 max-w-2xl mx-auto font-sans leading-relaxed">
            AEGIS continuously patrols the open web, unlocks hard-to-reach domains, indexes findings into persistent cognitive memory graphs, and dispatches automated response dispatches. 
          </p>

          {/* CTA Launch Button */}
          <div className="pt-6">
            <Link href="/dashboard" className="group relative inline-flex items-center justify-center p-0.5 mb-2 overflow-hidden text-sm font-medium rounded-lg group bg-gradient-to-br from-cyan-500 to-indigo-600 hover:text-white text-white focus:ring-4 focus:outline-none focus:ring-cyan-800 transition-all duration-300">
              <span className="relative px-8 py-3.5 transition-all ease-in duration-75 bg-[#050508] rounded-md group-hover:bg-opacity-0 font-mono tracking-wider flex items-center space-x-2">
                <span>LAUNCH COMMAND CENTER</span>
                <ArrowRight className="w-4 h-4 text-cyan-400 group-hover:text-white group-hover:translate-x-1 transition-all" />
              </span>
            </Link>
          </div>
        </motion.div>

        {/* Feature Grid icons stubs */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-16 max-w-3xl w-full">
          {[
            { label: "Bright Data Access", detail: "SERP + Web Unlocker", icon: GitBranch },
            { label: "Cognee Memory", detail: "Persistent Graph", icon: Shield },
            { label: "TriggerWare", detail: "Webhook Alerts", icon: Activity },
            { label: "AI/ML API", detail: "Model Routing", icon: Terminal },
          ].map((feat, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 * i, duration: 0.5 }}
              className="glass-card p-4 rounded-xl flex flex-col items-center justify-center text-center space-y-1.5 border border-white/5"
            >
              <div className="p-2 rounded-lg bg-white/5 border border-white/10 text-white/60">
                <feat.icon className="w-4 h-4" />
              </div>
              <h3 className="text-xs font-bold text-white font-mono">{feat.label}</h3>
              <p className="text-[10px] text-white/40">{feat.detail}</p>
            </motion.div>
          ))}
        </div>
      </main>

      {/* Footer bar */}
      <footer className="relative z-10 w-full max-w-7xl mx-auto px-6 py-6 flex items-center justify-between border-t border-white/5 text-white/30 text-xs font-mono">
        <span>AEGIS v1.0.0 // WEB DATA UNLOCKED HACKATHON</span>
        <span>DEADLINE: MAY 31, 2026</span>
      </footer>
    </div>
  );
}
