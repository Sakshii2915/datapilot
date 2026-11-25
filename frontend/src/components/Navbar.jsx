import React from 'react';
import { Database, ShieldCheck, Cpu, RefreshCw, Terminal } from 'lucide-react';

export default function Navbar({ health, onRefreshSchema, isRefreshing }) {
  const isHealthy = health?.status === 'healthy';
  const isMock = health?.llm_mode?.includes('Mock');

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-950/70 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand */}
      <div className="flex items-center space-x-3">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 p-0.5 shadow-lg shadow-indigo-500/20 flex items-center justify-center">
          <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
            <Database className="w-5 h-5 text-indigo-400" />
          </div>
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-300 bg-clip-text text-transparent">
              DataPilot
            </span>
            <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              v{health?.version || '1.0'}
            </span>
          </div>
          <p className="text-xs text-slate-400 hidden sm:block">Natural Language to SQL Analytics Agent</p>
        </div>
      </div>

      {/* Badges & System Status */}
      <div className="flex items-center space-x-3">
        {/* Database Status */}
        <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs">
          <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`} />
          <span className="text-slate-300 font-medium">{health?.database_type || 'Database'}</span>
        </div>

        {/* SQL Security Badge */}
        <div className="hidden md:flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>SQLGlot AST Guard</span>
        </div>

        {/* LLM Mode */}
        <div className={`hidden sm:flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs border ${
          isMock 
            ? 'bg-amber-500/10 border-amber-500/20 text-amber-300' 
            : 'bg-indigo-500/10 border-indigo-500/20 text-indigo-300'
        }`}>
          <Cpu className="w-3.5 h-3.5" />
          <span>{health?.llm_mode || 'LLM Engine'}</span>
        </div>

        {/* Refresh Schema Button */}
        <button
          onClick={onRefreshSchema}
          disabled={isRefreshing}
          title="Refresh database schema cache"
          className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-indigo-400' : ''}`} />
        </button>
      </div>
    </header>
  );
}
