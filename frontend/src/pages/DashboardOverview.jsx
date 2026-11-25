import React from 'react';
import { 
  Sparkles, 
  DollarSign, 
  ShoppingCart, 
  Users, 
  TrendingUp, 
  ShieldCheck, 
  ArrowRight,
  Database,
  Cpu,
  Layers,
  ChevronRight
} from 'lucide-react';

const FEATURED_PROMPTS = [
  {
    title: "Top 5 Products by Revenue",
    question: "What are the top 5 products by revenue?",
    category: "Product Performance",
    badge: "Aggregations & Joins"
  },
  {
    title: "Regional Sales Breakdown",
    question: "Which region generated the highest sales?",
    category: "Geographic Analytics",
    badge: "Grouping & Filters"
  },
  {
    title: "Monthly Revenue Trajectory",
    question: "Show monthly revenue for the last 12 months.",
    category: "Time Series",
    badge: "Date Truncation"
  },
  {
    title: "Top Customers by Total Spending",
    question: "Show the top 10 customers by total spending.",
    category: "Customer Analytics",
    badge: "Multi-Table JOIN"
  },
  {
    title: "Sales Across Categories",
    question: "Compare sales across different product categories.",
    category: "Category Analytics",
    badge: "SUM & Group By"
  },
  {
    title: "Average Order Value (AOV)",
    question: "What is the average order value?",
    category: "Executive Metrics",
    badge: "AVG Aggregation"
  },
];

export default function DashboardOverview({ onSelectPrompt, onNavigateTab, history = [] }) {
  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Welcome Hero Banner */}
      <div className="relative overflow-hidden bg-gradient-to-r from-indigo-950/60 via-slate-900 to-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous GenAI Analytics Engine</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
            Transform Natural Language into Validated, Safe SQL Queries
          </h1>
          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
            DataPilot connects to structured e-commerce databases, inspects dynamic schemas, generates PostgreSQL queries via LLM, enforces SQLGlot AST validation, and delivers natural language business insights.
          </p>
          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={() => onNavigateTab('assistant')}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm flex items-center space-x-2 shadow-lg shadow-indigo-600/25 transition"
            >
              <span>Open AI Assistant</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onNavigateTab('schema')}
              className="px-5 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-200 border border-slate-700 font-medium text-sm flex items-center space-x-2 transition"
            >
              <Database className="w-4 h-4 text-indigo-400" />
              <span>Explore Database Schema</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Sales</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-white font-mono">$102,480+</div>
            <p className="text-xs text-slate-400 mt-0.5">Aggregated across 120 orders</p>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Orders Tracked</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <ShoppingCart className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-white font-mono">120 Orders</div>
            <p className="text-xs text-slate-400 mt-0.5">Across 14 months of history</p>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Customer Base</span>
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-white font-mono">30 Customers</div>
            <p className="text-xs text-slate-400 mt-0.5">5 major geographic regions</p>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Merchandise Catalog</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-white font-mono">27 Products</div>
            <p className="text-xs text-slate-400 mt-0.5">7 core e-commerce categories</p>
          </div>
        </div>
      </div>

      {/* Featured Analytics Questions Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">Curated Analytics Inquiries</h2>
            <p className="text-xs text-slate-400">Click any card to trigger the natural language query pipeline.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURED_PROMPTS.map((prompt, idx) => (
            <div
              key={idx}
              onClick={() => onSelectPrompt(prompt.question)}
              className="group p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-indigo-500/40 hover:bg-slate-900 cursor-pointer transition shadow-md flex flex-col justify-between space-y-4"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-indigo-400 font-semibold">{prompt.category}</span>
                  <span className="px-2 py-0.5 rounded-md bg-slate-800 text-[10px] text-slate-400 font-mono">
                    {prompt.badge}
                  </span>
                </div>
                <h3 className="text-sm font-semibold text-white group-hover:text-indigo-300 transition leading-snug">
                  "{prompt.question}"
                </h3>
              </div>
              <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/60">
                <span className="group-hover:text-slate-300 transition">Execute pipeline</span>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-1 group-hover:text-indigo-400 transition" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Security Architecture Callout */}
      <div className="rounded-2xl p-6 bg-slate-900 border border-slate-800 space-y-4">
        <div className="flex items-center space-x-2 text-emerald-400 font-semibold text-sm">
          <ShieldCheck className="w-5 h-5" />
          <span>Multi-Layer SQL Security Architecture</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-300">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <span className="font-semibold text-white">1. SQLGlot AST Parsing</span>
            <p className="text-slate-400 leading-relaxed">
              Validates SQL abstract syntax trees to strictly prohibit INSERT, UPDATE, DELETE, DROP, ALTER, and stacked queries.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <span className="font-semibold text-white">2. Read-Only Account Access</span>
            <p className="text-slate-400 leading-relaxed">
              Executes generated queries against a dedicated PostgreSQL database role granted exclusively SELECT privileges.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <span className="font-semibold text-white">3. Guardrails & Timeouts</span>
            <p className="text-slate-400 leading-relaxed">
              Injects LIMIT clamps (max 100 rows) and statement timeouts (10s) to prevent memory exhaustion and runaway joins.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
