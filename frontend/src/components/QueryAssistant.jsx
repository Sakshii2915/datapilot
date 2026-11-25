import React, { useState } from 'react';
import { 
  Sparkles, 
  Send, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldCheck, 
  Clock, 
  Copy, 
  Check, 
  Layers, 
  ArrowRight,
  Database,
  Terminal,
  HelpCircle,
  BarChart3,
  Table as TableIcon
} from 'lucide-react';

const EXAMPLE_QUESTIONS = [
  "What are the top 5 products by revenue?",
  "Which region generated the highest sales?",
  "Show monthly revenue for the last 12 months.",
  "Which customers have placed the most orders?",
  "Compare sales across different product categories.",
  "What is the average order value?",
  "Show the top 10 customers by total spending.",
];

export default function QueryAssistant({ 
  queryResult, 
  isLoading, 
  onSubmitQuery, 
  onNavigateTab 
}) {
  const [inputQuestion, setInputQuestion] = useState('');
  const [copied, setCopied] = useState(false);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!inputQuestion.trim() || isLoading) return;
    onSubmitQuery(inputQuestion);
  };

  const handleSelectExample = (q) => {
    setInputQuestion(q);
    onSubmitQuery(q);
  };

  const handleCopySQL = () => {
    if (queryResult?.generated_sql) {
      navigator.clipboard.writeText(queryResult.generated_sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Pipeline execution stages
  const pipelineStages = [
    { name: 'Schema Context', done: !isLoading && !!queryResult },
    { name: 'LLM SQL Generation', done: !isLoading && !!queryResult?.generated_sql },
    { name: 'SQLGlot AST Security', done: !isLoading && (queryResult?.execution_status === 'success' || queryResult?.execution_status === 'rejected') },
    { name: 'Read-Only Execution', done: !isLoading && queryResult?.execution_status === 'success' },
    { name: 'AI Result Explanation', done: !isLoading && !!queryResult?.explanation },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Question Input Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />
        
        <div className="flex items-center space-x-2 text-indigo-400 font-semibold text-sm mb-3">
          <Sparkles className="w-4 h-4" />
          <span>Ask Database in Natural Language</span>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative flex items-center">
            <input
              type="text"
              value={inputQuestion}
              onChange={(e) => setInputQuestion(e.target.value)}
              placeholder="e.g. What are the top 5 products by revenue?"
              disabled={isLoading}
              className="w-full bg-slate-950/80 border border-slate-700/80 rounded-xl px-4 py-3.5 pr-28 text-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
            />
            <button
              type="submit"
              disabled={isLoading || !inputQuestion.trim()}
              className="absolute right-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center space-x-2 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-indigo-600/20"
            >
              {isLoading ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <span>Run Agent</span>
                  <Send className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>

          {/* Quick Example Chips */}
          <div className="flex items-center space-x-2 overflow-x-auto pb-1 pt-1 text-xs text-slate-400 scrollbar-none">
            <span className="shrink-0 text-slate-400 font-medium">Try asking:</span>
            {EXAMPLE_QUESTIONS.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectExample(q)}
                className="shrink-0 px-3 py-1 rounded-full bg-slate-800/80 hover:bg-indigo-600/20 hover:text-indigo-300 border border-slate-700/50 hover:border-indigo-500/30 text-slate-300 transition"
              >
                {q}
              </button>
            ))}
          </div>
        </form>
      </div>

      {/* Pipeline Visualizer (When Loading or Result Present) */}
      {(isLoading || queryResult) && (
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3 text-xs text-slate-400 font-medium">
            <span className="flex items-center space-x-1.5">
              <Layers className="w-3.5 h-3.5 text-indigo-400" />
              <span>Multi-Agent GenAI Execution Pipeline</span>
            </span>
            {queryResult?.is_mock && (
              <span className="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 font-mono text-[11px]">
                Mock LLM Engine (Fallback Mode)
              </span>
            )}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
            {pipelineStages.map((st, i) => (
              <div 
                key={i}
                className={`p-2.5 rounded-lg border text-xs flex items-center space-x-2 ${
                  st.done
                    ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300'
                    : isLoading
                    ? 'bg-indigo-950/20 border-indigo-500/30 text-indigo-300 animate-pulse'
                    : 'bg-slate-950/40 border-slate-800 text-slate-400'
                }`}
              >
                <div className={`w-2 h-2 rounded-full shrink-0 ${st.done ? 'bg-emerald-400' : isLoading ? 'bg-indigo-400' : 'bg-slate-600'}`} />
                <span className="truncate">{st.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Query Result Displays */}
      {queryResult && (
        <div className="space-y-5">
          {/* Status Header */}
          <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900 border border-slate-800 rounded-xl px-5 py-3">
            <div className="flex items-center space-x-3">
              <span className={`px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider flex items-center space-x-1.5 ${
                queryResult.execution_status === 'success'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : queryResult.execution_status === 'rejected'
                  ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                  : queryResult.execution_status === 'clarification_needed'
                  ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
              }`}>
                {queryResult.execution_status === 'success' ? (
                  <CheckCircle2 className="w-3.5 h-3.5" />
                ) : (
                  <AlertTriangle className="w-3.5 h-3.5" />
                )}
                <span>Status: {queryResult.execution_status}</span>
              </span>

              {queryResult.execution_status === 'success' && (
                <>
                  <span className="text-xs text-slate-400 flex items-center space-x-1">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span>{queryResult.execution_time_ms} ms</span>
                  </span>
                  <span className="text-xs text-slate-400">•</span>
                  <span className="text-xs text-slate-400">
                    <strong className="text-white font-mono">{queryResult.row_count}</strong> rows returned
                  </span>
                </>
              )}

              {queryResult.correction_attempts > 0 && (
                <span className="text-xs px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-300">
                  Fixed in {queryResult.correction_attempts} correction attempt(s)
                </span>
              )}
            </div>

            {/* Quick jump to Tables or Charts */}
            {queryResult.execution_status === 'success' && queryResult.row_count > 0 && (
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => onNavigateTab('explorer')}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 flex items-center space-x-1.5 transition"
                >
                  <TableIcon className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Inspect Data Table</span>
                </button>
                <button
                  onClick={() => onNavigateTab('analytics')}
                  className="px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-xs font-medium text-indigo-300 flex items-center space-x-1.5 transition"
                >
                  <BarChart3 className="w-3.5 h-3.5 text-indigo-400" />
                  <span>View Visual Charts</span>
                </button>
              </div>
            )}
          </div>

          {/* Clarification Needed Alert */}
          {queryResult.clarification_needed && (
            <div className="bg-amber-950/20 border border-amber-500/30 rounded-xl p-5 text-amber-200">
              <div className="flex items-start space-x-3">
                <HelpCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-sm text-amber-300 mb-1">Clarification Required</h4>
                  <p className="text-sm text-amber-200/90 leading-relaxed">
                    {queryResult.clarification_needed}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Security Rejection or Error Alert */}
          {queryResult.error_message && (
            <div className="bg-rose-950/20 border border-rose-500/30 rounded-xl p-5 text-rose-200">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-sm text-rose-300 mb-1">Execution Blocked / Error</h4>
                  <p className="text-sm text-rose-200/90 font-mono leading-relaxed">
                    {queryResult.error_message}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Natural Language Result Explanation Card */}
          {queryResult.explanation && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md">
              <div className="flex items-center space-x-2 text-indigo-400 font-semibold text-xs uppercase tracking-wider mb-2">
                <Sparkles className="w-4 h-4" />
                <span>Executive Insights & Findings</span>
              </div>
              <div className="text-slate-200 text-sm leading-relaxed whitespace-pre-line font-normal">
                {queryResult.explanation}
              </div>
            </div>
          )}

          {/* Generated SQL Block with Syntax Highlighting & Copy */}
          {queryResult.generated_sql && (
            <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-md">
              <div className="bg-slate-900/80 px-4 py-2.5 border-b border-slate-800 flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2 text-slate-300 font-mono">
                  <Terminal className="w-3.5 h-3.5 text-indigo-400" />
                  <span>PostgreSQL Generated Query</span>
                  <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] border border-emerald-500/20">
                    AST Validated
                  </span>
                </div>
                <button
                  onClick={handleCopySQL}
                  className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center space-x-1 transition"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  <span>{copied ? 'Copied!' : 'Copy SQL'}</span>
                </button>
              </div>
              <pre className="p-4 text-xs font-mono text-indigo-200 overflow-x-auto leading-relaxed">
                <code>{queryResult.generated_sql}</code>
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
