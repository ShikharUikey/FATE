"use client";

import React, { useState, useEffect, useRef } from "react";

interface LogEntry {
  time: string;
  source: string;
  message: string;
  type: "info" | "success" | "warning" | "error";
}

export default function FateConsole() {
  const [query, setQuery] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [voiceActive, setVoiceActive] = useState(false);
  const [status, setStatus] = useState("CONNECTED");
  const [logs, setLogs] = useState<LogEntry[]>([
    { time: "22:50:00", source: "SYSTEM", message: "FATE Core ASGI daemon initialized", type: "info" },
    { time: "22:50:01", source: "DATABASE", message: "SQLite WAL engine mode configured successfully", type: "success" },
    { time: "22:50:01", source: "MEMORY", message: "Local Qdrant in-memory client collections generated", type: "success" },
    { time: "22:50:02", source: "VOICE", message: "Offline speech recognition Whispertiny engine verified", type: "info" },
    { time: "22:50:02", source: "ORCHESTRATOR", message: "Agent dispatch gateways registered (Desktop, FileSystem, Browser)", type: "success" }
  ]);
  
  const logEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logs window
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const addLog = (source: string, message: string, type: "info" | "success" | "warning" | "error" = "info") => {
    const time = new Date().toTimeString().split(" ")[0];
    setLogs((prev) => [...prev, { time, source, message, type }]);
  };

  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isProcessing) return;

    setIsProcessing(true);
    addLog("USER", `Command submitted: "${query}"`, "info");
    
    // Simulate FATE Core planning DAG processing
    setTimeout(() => {
      addLog("BRAIN", "Classified intent: CreateMeetingAndEmail", "success");
      addLog("ORCHESTRATOR", "Plan generated: Task 0 (CalendarAgent) -> Task 1 (CommunicationAgent)", "info");
      
      setTimeout(() => {
        addLog("CALENDAR_AGENT", "Successfully scheduled meeting with Bob at 10:00 AM", "success");
        
        setTimeout(() => {
          addLog("COMMUNICATION_AGENT", "Email confirmation sent to bob@example.com", "success");
          addLog("SYSTEM", "All scheduled tasks completed successfully.", "success");
          setIsProcessing(false);
          setQuery("");
        }, 1200);
      }, 1000);
    }, 800);
  };

  const toggleVoiceTrigger = () => {
    if (voiceActive) {
      setVoiceActive(false);
      addLog("VOICE", "Voice stream session closed", "info");
    } else {
      setVoiceActive(true);
      addLog("VOICE", "Wake word detected. Listening for PCM chunks on /ws/voice...", "warning");
      
      // Simulate voice input transcription after a brief delay
      setTimeout(() => {
        if (!voiceActive) {
          addLog("STT", 'Transcribed speech: "scan my directory for duplicate files"', "success");
          addLog("BRAIN", "Classified intent: FileSystemDuplicatesPrune", "success");
          addLog("FILESYSTEM_AGENT", "Deleted duplicates: test_sandbox/copy1.txt, copy2.txt", "success");
          setVoiceActive(false);
        }
      }, 4000);
    }
  };

  return (
    <main className="min-h-screen p-6 md:p-12 flex flex-col justify-between max-w-7xl mx-auto">
      
      {/* Top Header Section */}
      <header className="flex flex-col sm:flex-row justify-between items-center gap-4 mb-8 pb-6 border-b border-gray-800">
        <div>
          <h1 className="text-3xl font-bold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-violet-500 via-purple-500 to-cyan-500">
            FATE CORE
          </h1>
          <p className="text-xs text-gray-400 mt-1 uppercase tracking-widest font-mono">
            Fully Automated Task Executive Console
          </p>
        </div>
        <div className="flex items-center gap-3 bg-gray-900/60 px-4 py-2 rounded-xl border border-gray-800">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
          </span>
          <span className="text-xs font-mono text-cyan-400">
            LOOPBACK: 127.0.0.1:8000
          </span>
        </div>
      </header>

      {/* Main Panel grid */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch flex-grow">
        
        {/* Left Control Board (5 Cols) */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          
          {/* Glassmorphic Query Form */}
          <div className="glass-panel p-6 flex flex-col gap-4">
            <h2 className="text-lg font-medium text-gray-200">Execution Prompt</h2>
            <form onSubmit={handleQuerySubmit} className="flex flex-col gap-3">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Type your command or request..."
                disabled={isProcessing}
                className="glow-input"
              />
              <button
                type="submit"
                disabled={isProcessing}
                className="w-full py-3.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-medium rounded-xl transition duration-300 shadow-lg shadow-indigo-950/50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessing ? "PROCESSING PLAN..." : "DISPATCH COMMAND"}
              </button>
            </form>
          </div>

          {/* Voice Orb Trigger */}
          <div className="glass-panel p-6 flex flex-col items-center justify-center text-center gap-6">
            <div>
              <h2 className="text-lg font-medium text-gray-200">Voice Activation</h2>
              <p className="text-xs text-gray-400 mt-1">Tap to speak or start offline transcribers</p>
            </div>
            
            <button
              onClick={toggleVoiceTrigger}
              className={`w-28 h-28 rounded-full flex items-center justify-center transition-all duration-500 relative border ${
                voiceActive 
                  ? "bg-rose-500/20 border-rose-500 pulse-glow shadow-rose-950/50" 
                  : "bg-violet-600/10 border-violet-500/30 hover:border-violet-500 shadow-violet-950/20"
              }`}
              style={{
                boxShadow: voiceActive 
                  ? "0 0 30px rgba(239, 68, 68, 0.4)" 
                  : "0 8px 32px 0 rgba(139, 92, 246, 0.15)"
              }}
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                className={`w-8 h-8 transition-all ${voiceActive ? "text-rose-400 scale-110" : "text-violet-400"}`}
              >
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                <path d="M19 10v1a7 7 0 0 1-14 0v-1"></path>
                <line x1="12" x2="12" y1="19" y2="22"></line>
              </svg>
            </button>

            <span className={`text-xs font-mono tracking-widest uppercase transition-colors ${voiceActive ? "text-rose-400" : "text-violet-400"}`}>
              {voiceActive ? "LISTENING..." : "STANDBY"}
            </span>
          </div>

          {/* System Status Indicators */}
          <div className="glass-panel p-6 grid grid-cols-2 gap-4">
            <div className="bg-white/[0.02] border border-white/[0.04] p-4 rounded-xl">
              <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">DATABASE WAL</span>
              <p className="text-sm font-medium text-emerald-400 mt-1">ONLINE</p>
            </div>
            <div className="bg-white/[0.02] border border-white/[0.04] p-4 rounded-xl">
              <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">MEMORY VECTORS</span>
              <p className="text-sm font-medium text-violet-400 mt-1">2 COLLECTIONS</p>
            </div>
            <div className="bg-white/[0.02] border border-white/[0.04] p-4 rounded-xl">
              <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">LLM BACKEND</span>
              <p className="text-sm font-medium text-cyan-400 mt-1">LOCAL FALLBACK</p>
            </div>
            <div className="bg-white/[0.02] border border-white/[0.04] p-4 rounded-xl">
              <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">ACTIVE DRIVERS</span>
              <p className="text-sm font-medium text-gray-300 mt-1">COCOA + POSIX</p>
            </div>
          </div>

        </div>

        {/* Right Terminal Log Board (7 Cols) */}
        <div className="lg:col-span-7 glass-panel flex flex-col h-[520px] lg:h-auto">
          <div className="flex justify-between items-center px-6 py-4 border-b border-white/[0.04] bg-white/[0.01]">
            <span className="text-xs uppercase tracking-widest font-mono text-gray-400">Execution Traces & Logs</span>
            <button 
              onClick={() => setLogs([])}
              className="text-[10px] uppercase font-mono text-violet-400 hover:text-violet-300 transition"
            >
              Clear Buffer
            </button>
          </div>
          
          {/* Scrollable logs area */}
          <div className="flex-grow p-6 overflow-y-auto font-mono text-xs flex flex-col gap-3.5 bg-black/20">
            {logs.map((log, i) => (
              <div key={i} className="flex items-start gap-3 leading-relaxed">
                <span className="text-gray-600 select-none">{log.time}</span>
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold tracking-wider select-none ${
                  log.type === "success" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" :
                  log.type === "warning" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" :
                  log.type === "error" ? "bg-rose-500/10 text-rose-400 border border-rose-500/20" :
                  "bg-violet-500/10 text-violet-400 border border-violet-500/20"
                }`}>
                  {log.source}
                </span>
                <span className={
                  log.type === "success" ? "text-emerald-300" :
                  log.type === "warning" ? "text-amber-300" :
                  log.type === "error" ? "text-rose-300" :
                  "text-gray-300"
                }>
                  {log.message}
                </span>
              </div>
            ))}
            <div ref={logEndRef} />
          </div>
        </div>

      </section>

      {/* Footer copyright */}
      <footer className="mt-8 text-center text-[10px] text-gray-500 uppercase tracking-widest font-mono">
        Project FATE Core — Platform v0.1.0 (macOS Sequoia Apple Silicon)
      </footer>

    </main>
  );
}
