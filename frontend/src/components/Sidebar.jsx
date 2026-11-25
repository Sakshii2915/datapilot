import React from 'react';
import { 
  LayoutDashboard, 
  Sparkles, 
  Table, 
  BarChart3, 
  Database, 
  History,
  ShieldAlert,
  GitBranch
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, historyCount = 0 }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'assistant', label: 'AI Query Assistant', icon: Sparkles, badge: 'Agent' },
    { id: 'explorer', label: 'Results Explorer', icon: Table },
    { id: 'analytics', label: 'Visual Analytics', icon: BarChart3 },
    { id: 'schema', label: 'Schema Explorer', icon: Database },
    { id: 'history', label: 'Query History', icon: History, count: historyCount },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 flex flex-col justify-between shrink-0 h-[calc(100vh-4rem)]">
      {/* Navigation Links */}
      <div className="p-4 space-y-1">
        <div className="px-3 py-2 text-[11px] font-semibold tracking-wider uppercase text-slate-400">
          Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 shadow-sm shadow-indigo-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300">
                  {item.badge}
                </span>
              )}
              {item.count !== undefined && item.count > 0 && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
                  {item.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Architecture Architecture pill & security footer */}
      <div className="p-4 border-t border-slate-900 bg-slate-950/50">
        <div className="rounded-xl p-3 bg-slate-900/60 border border-slate-800/80 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-300 font-medium">
            <span className="flex items-center space-x-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-emerald-400" />
              <span>Safe Execution</span>
            </span>
            <span className="text-[10px] text-emerald-400 font-mono">RO Account</span>
          </div>
          <div className="text-[11px] text-slate-400 leading-relaxed">
            SQLGlot AST restricts to read-only SELECT with query limits & timeouts.
          </div>
        </div>
      </div>
    </aside>
  );
}
