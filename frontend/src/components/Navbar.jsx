import React, { useState, useEffect } from 'react';
import { Menu, Sparkles, Server, CheckCircle2, AlertCircle } from 'lucide-react';
import axios from 'axios';

export default function Navbar({ setMobileOpen, onOpenAssistant, pageTitle }) {
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    let mounted = true;
    axios.get('/api/health')
      .then(res => {
        if (mounted) {
          setBackendStatus(res.data.status === 'healthy' ? 'online' : 'degraded');
        }
      })
      .catch(() => {
        if (mounted) setBackendStatus('offline');
      });
    return () => { mounted = false; };
  }, []);

  return (
    <header className="h-16 bg-slate-900/60 backdrop-blur-md border-b border-slate-800 sticky top-0 z-30 flex items-center justify-between px-4 lg:px-8">
      <div className="flex items-center gap-3">
        <button
          onClick={() => setMobileOpen(true)}
          className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-base font-semibold text-white tracking-tight">{pageTitle || 'Student Insight AI'}</h1>
          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            <span>OULAD Production Environment</span>
            <span>•</span>
            <span className="text-sky-400 font-mono">Cohort 2014J</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Backend Status indicator */}
        <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/80 text-xs">
          <Server className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-400 font-medium">Gateway:</span>
          {backendStatus === 'online' ? (
            <span className="flex items-center gap-1 text-emerald-400 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Connected
            </span>
          ) : backendStatus === 'checking' ? (
            <span className="text-slate-400">Checking...</span>
          ) : (
            <span className="flex items-center gap-1 text-rose-400 font-medium">
              <AlertCircle className="w-3 h-3" />
              Service Offline
            </span>
          )}
        </div>

        {/* AI Assistant Quick Toggle Button */}
        <button
          onClick={onOpenAssistant}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-xs transition shadow-sm shadow-sky-500/20 active:scale-95"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span className="hidden md:inline">Ask Insight AI</span>
        </button>
      </div>
    </header>
  );
}
