import React, { useState } from 'react';
import { 
  Database, 
  Key, 
  Link2, 
  Table2, 
  RefreshCw, 
  Hash, 
  Tag, 
  Layers,
  ArrowRight
} from 'lucide-react';

export default function SchemaExplorer({ schema, onRefreshSchema, isRefreshing }) {
  const tables = schema?.tables || [];
  const relationships = schema?.relationships || [];
  const [selectedTableName, setSelectedTableName] = useState(tables[0]?.name || 'customers');

  const selectedTable = tables.find((t) => t.name === selectedTableName) || tables[0];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900 border border-slate-800 rounded-xl p-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-white">Database Schema Intelligence</h2>
            <p className="text-xs text-slate-400">{schema?.schema_summary || 'Dynamic database schema'}</p>
          </div>
        </div>

        <button
          onClick={onRefreshSchema}
          disabled={isRefreshing}
          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center space-x-1.5 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-indigo-400' : ''}`} />
          <span>Refresh Metadata</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Table Selector Cards */}
        <div className="lg:col-span-1 space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 px-1 mb-2">
            Discovered Tables ({tables.length})
          </div>
          <div className="space-y-1.5">
            {tables.map((tbl) => {
              const isSelected = tbl.name === selectedTable?.name;
              return (
                <button
                  key={tbl.name}
                  onClick={() => setSelectedTableName(tbl.name)}
                  className={`w-full text-left p-3 rounded-xl border transition flex items-center justify-between ${
                    isSelected
                      ? 'bg-indigo-600/10 border-indigo-500/40 text-white shadow-sm'
                      : 'bg-slate-900/60 border-slate-800/80 text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Table2 className={`w-4 h-4 ${isSelected ? 'text-indigo-400' : 'text-slate-400'}`} />
                    <span className="text-sm font-medium">{tbl.name}</span>
                  </div>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-slate-950 text-slate-400 font-mono">
                    {tbl.row_count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Table Deep Dive */}
        <div className="lg:col-span-3 space-y-4">
          {selectedTable ? (
            <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
              {/* Table Info Banner */}
              <div className="bg-slate-900/80 px-6 py-4 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-bold text-white font-mono">{selectedTable.name}</h3>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-mono">
                      {selectedTable.row_count} records
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {selectedTable.columns.length} columns defined • {selectedTable.primary_keys.length} Primary Key
                  </p>
                </div>
              </div>

              {/* Columns Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-900/50 border-b border-slate-800 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                    <tr>
                      <th className="py-2.5 px-4">Column Name</th>
                      <th className="py-2.5 px-4">Data Type</th>
                      <th className="py-2.5 px-4">Key / Reference</th>
                      <th className="py-2.5 px-4">Nullable</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {selectedTable.columns.map((col) => (
                      <tr key={col.name} className="hover:bg-slate-900/30 transition">
                        <td className="py-2.5 px-4 font-semibold text-white">
                          <div className="flex items-center space-x-1.5">
                            {col.primary_key && <Key className="w-3.5 h-3.5 text-amber-400" />}
                            {col.foreign_key && <Link2 className="w-3.5 h-3.5 text-cyan-400" />}
                            <span>{col.name}</span>
                          </div>
                        </td>
                        <td className="py-2.5 px-4 text-indigo-300">{col.type}</td>
                        <td className="py-2.5 px-4">
                          {col.primary_key ? (
                            <span className="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[10px]">
                              PRIMARY KEY
                            </span>
                          ) : col.foreign_key ? (
                            <span className="px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-[10px]">
                              FK → {col.foreign_key}
                            </span>
                          ) : (
                            <span className="text-slate-400 font-sans text-[11px]">—</span>
                          )}
                        </td>
                        <td className="py-2.5 px-4 text-slate-400 font-sans">
                          {col.nullable ? 'YES' : 'NO'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Sample Categorical Values */}
              {selectedTable.sample_values && Object.keys(selectedTable.sample_values).length > 0 && (
                <div className="p-5 border-t border-slate-800 bg-slate-900/30 space-y-3">
                  <div className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5 uppercase tracking-wider">
                    <Tag className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Distinct High-Signal Values (Used by Prompt Engine)</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {Object.entries(selectedTable.sample_values).map(([colName, vals]) => (
                      <div key={colName} className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1.5">
                        <span className="text-xs font-mono text-indigo-300 font-semibold">{colName}:</span>
                        <div className="flex flex-wrap gap-1">
                          {vals.map((v, i) => (
                            <span key={i} className="text-[11px] px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300">
                              {String(v)}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 text-center text-slate-400 bg-slate-900 rounded-xl border border-slate-800">
              Select a table from the left to view its schema details.
            </div>
          )}

          {/* Relational Join Paths Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center space-x-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              <span>Foreign Key Relationships & Join Topology</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono">
              {relationships.map((rel, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between text-slate-300">
                  <span className="text-indigo-300">{rel.source_table}.{rel.source_column}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-400 mx-2 shrink-0" />
                  <span className="text-cyan-300">{rel.target_table}.{rel.target_column}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
