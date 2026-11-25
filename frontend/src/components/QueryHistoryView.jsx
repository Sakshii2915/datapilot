import React, { useState } from 'react';
import { 
  History, 
  Trash2, 
  Play, 
  Clock, 
  Terminal, 
  CheckCircle2, 
  AlertTriangle, 
  FileCode,
  Check,
  Copy
} from 'lucide-react';

export default function QueryHistoryView({ 
  history, 
  onRunQuestion, 
  onDeleteHistoryItem, 
  onClearAllHistory 
}) {
  const [selectedSQL, setSelectedSQL] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleCopy = (sql) => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-4 max-w-7xl mx-auto">
      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900 border border-slate-800 rounded-xl p-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
            <History className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-white">Query Execution Log</h2>
            <p className="text-xs text-slate-400">
              Audit log of natural language questions, generated SQL, execution metrics, and security evaluations.
            </p>
          </div>
        </div>

        {history.length > 0 && (
          <button
            onClick={onClearAllHistory}
            className="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-medium flex items-center space-x-1.5 transition"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear History</span>
          </button>
        )}
      </div>

      {/* History Items List */}
      {history.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center max-w-4xl mx-auto my-8">
          <History className="w-12 h-12 text-slate-400 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-white mb-1">No Query History Recorded</h3>
          <p className="text-sm text-slate-400 max-w-md mx-auto">
            Questions asked in the AI Query Assistant will be automatically logged here for inspection and reproduction.
          </p>
        </div>
      ) : (
        <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <div className="divide-y divide-slate-800/80">
            {history.map((item) => (
              <div 
                key={item.id}
                className="p-4 hover:bg-slate-900/40 transition flex flex-col md:flex-row md:items-center justify-between gap-3"
              >
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider flex items-center space-x-1 ${
                      item.execution_status === 'success'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : item.execution_status === 'rejected'
                        ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {item.execution_status === 'success' ? (
                        <CheckCircle2 className="w-3 h-3" />
                      ) : (
                        <AlertTriangle className="w-3 h-3" />
                      )}
                      <span>{item.execution_status}</span>
                    </span>

                    <span className="text-xs text-slate-400">
                      {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>

                    {item.execution_time_ms > 0 && (
                      <span className="text-xs text-slate-400 font-mono flex items-center space-x-1">
                        <Clock className="w-3 h-3 text-slate-400" />
                        <span>{item.execution_time_ms} ms</span>
                      </span>
                    )}

                    {item.row_count > 0 && (
                      <span className="text-xs text-slate-400 font-mono">
                        {item.row_count} rows
                      </span>
                    )}
                  </div>

                  <h4 className="text-sm font-medium text-white truncate">
                    {item.question}
                  </h4>

                  {item.natural_language_explanation && (
                    <p className="text-xs text-slate-400 line-clamp-1">
                      {item.natural_language_explanation}
                    </p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2 shrink-0">
                  {item.generated_sql && (
                    <button
                      onClick={() => setSelectedSQL(item.generated_sql)}
                      className="px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-xs text-slate-300 flex items-center space-x-1 border border-slate-800 transition"
                      title="Inspect Generated SQL"
                    >
                      <Terminal className="w-3.5 h-3.5 text-indigo-400" />
                      <span>View SQL</span>
                    </button>
                  )}

                  <button
                    onClick={() => onRunQuestion(item.question)}
                    className="px-2.5 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-xs text-indigo-300 flex items-center space-x-1 border border-indigo-500/30 transition"
                    title="Re-run Query"
                  >
                    <Play className="w-3.5 h-3.5" />
                    <span>Run</span>
                  </button>

                  <button
                    onClick={() => onDeleteHistoryItem(item.id)}
                    className="p-1.5 rounded-lg bg-slate-900 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 border border-slate-800 transition"
                    title="Delete Record"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SQL Preview Modal */}
      {selectedSQL && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-950 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2 text-white font-semibold text-sm">
                <Terminal className="w-4 h-4 text-indigo-400" />
                <span>Generated PostgreSQL Query</span>
              </div>
              <button
                onClick={() => setSelectedSQL(null)}
                className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded bg-slate-900 border border-slate-800"
              >
                Close
              </button>
            </div>

            <pre className="p-4 rounded-xl bg-slate-900 text-xs font-mono text-indigo-200 overflow-x-auto leading-relaxed border border-slate-800">
              <code>{selectedSQL}</code>
            </pre>

            <div className="flex justify-end">
              <button
                onClick={() => handleCopy(selectedSQL)}
                className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center space-x-1.5 transition"
              >
                {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied' : 'Copy to Clipboard'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
