import React, { useState, useMemo, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { 
  BarChart3, 
  LineChart as LineIcon, 
  PieChart as PieIcon, 
  AreaChart as AreaIcon,
  Layers,
  AlertCircle
} from 'lucide-react';

const COLORS = [
  '#6366f1', // Indigo
  '#06b6d4', // Cyan
  '#10b981', // Emerald
  '#f59e0b', // Amber
  '#ec4899', // Pink
  '#8b5cf6', // Purple
  '#3b82f6', // Blue
  '#14b8a6', // Teal
];

export default function VisualAnalytics({ queryResult }) {
  const columns = queryResult?.columns || [];
  const rows = queryResult?.rows || [];

  // Identify column data types
  const { categoricalCols, numericCols } = useMemo(() => {
    if (!rows.length || !columns.length) {
      return { categoricalCols: [], numericCols: [] };
    }
    const sample = rows[0];
    const cat = [];
    const num = [];

    columns.forEach((col) => {
      const val = sample[col];
      if (typeof val === 'number') {
        num.push(col);
      } else {
        cat.push(col);
      }
    });

    return { categoricalCols: cat, numericCols: num };
  }, [columns, rows]);

  // Determine initial best chart type and axis defaults
  const [chartType, setChartType] = useState('bar');
  const [xAxisKey, setXAxisKey] = useState('');
  const [yAxisKey, setYAxisKey] = useState('');

  useEffect(() => {
    if (categoricalCols.length > 0 && numericCols.length > 0) {
      const isDate = categoricalCols.some((c) =>
        c.toLowerCase().includes('date') || c.toLowerCase().includes('month') || c.toLowerCase().includes('day')
      );
      if (isDate) {
        setChartType('line');
        const dateCol = categoricalCols.find((c) =>
          c.toLowerCase().includes('date') || c.toLowerCase().includes('month')
        );
        setXAxisKey(dateCol || categoricalCols[0]);
      } else {
        setChartType('bar');
        setXAxisKey(categoricalCols[0]);
      }
      setYAxisKey(numericCols[0]);
    } else if (columns.length >= 2) {
      setXAxisKey(columns[0]);
      setYAxisKey(columns[1]);
    }
  }, [categoricalCols, numericCols, columns]);

  // Format chart data (top 20 points for readability)
  const chartData = useMemo(() => {
    return rows.slice(0, 20).map((r) => ({
      ...r,
      [xAxisKey]: String(r[xAxisKey] ?? ''),
      [yAxisKey]: typeof r[yAxisKey] === 'number' ? r[yAxisKey] : parseFloat(r[yAxisKey]) || 0,
    }));
  }, [rows, xAxisKey, yAxisKey]);

  if (!queryResult || queryResult.execution_status !== 'success' || rows.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center max-w-4xl mx-auto my-8">
        <BarChart3 className="w-12 h-12 text-slate-400 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-white mb-1">No Visual Data Available</h3>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          Execute an analytics query with aggregate metrics (e.g. revenue, order count) to generate interactive charts.
        </p>
      </div>
    );
  }

  const hasNumeric = numericCols.length > 0;

  return (
    <div className="space-y-4 max-w-7xl mx-auto">
      {/* Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-4">
        {/* Chart Type Selector */}
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider mr-1">
            Chart Type:
          </span>
          <div className="flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800 space-x-1">
            <button
              onClick={() => setChartType('bar')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 transition ${
                chartType === 'bar' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>Bar</span>
            </button>
            <button
              onClick={() => setChartType('line')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 transition ${
                chartType === 'line' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              <LineIcon className="w-3.5 h-3.5" />
              <span>Line</span>
            </button>
            <button
              onClick={() => setChartType('area')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 transition ${
                chartType === 'area' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              <AreaIcon className="w-3.5 h-3.5" />
              <span>Area</span>
            </button>
            <button
              onClick={() => setChartType('pie')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 transition ${
                chartType === 'pie' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              <PieIcon className="w-3.5 h-3.5" />
              <span>Pie</span>
            </button>
          </div>
        </div>

        {/* Axis Dimension & Metric Selectors */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-400">Dimension (X):</span>
            <select
              value={xAxisKey}
              onChange={(e) => setXAxisKey(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              {columns.map((col) => (
                <option key={col} value={col}>
                  {col}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-400">Metric (Y):</span>
            <select
              value={yAxisKey}
              onChange={(e) => setYAxisKey(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              {numericCols.length > 0 ? (
                numericCols.map((col) => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))
              ) : (
                columns.map((col) => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))
              )}
            </select>
          </div>
        </div>
      </div>

      {/* Chart Canvas Card */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-xl relative min-h-[440px] flex flex-col justify-center">
        {!hasNumeric ? (
          <div className="text-center py-12">
            <AlertCircle className="w-10 h-10 text-amber-400 mx-auto mb-2" />
            <h4 className="text-base font-semibold text-white">No Numeric Values to Chart</h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1">
              The returned dataset consists solely of text columns. To render numerical charts, ask a question involving revenue, sums, or counts.
            </p>
          </div>
        ) : (
          <div className="w-full h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              {chartType === 'bar' ? (
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis 
                    dataKey={xAxisKey} 
                    stroke="#64748b" 
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    angle={-35} 
                    textAnchor="end" 
                    interval={0}
                  />
                  <YAxis 
                    stroke="#64748b" 
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    tickFormatter={(val) => val >= 1000 ? `${(val / 1000).toFixed(1)}k` : val}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                    formatter={(val) => [typeof val === 'number' ? val.toLocaleString() : val, yAxisKey]}
                  />
                  <Legend wrapperStyle={{ paddingTop: '20px', fontSize: '12px' }} />
                  <Bar dataKey={yAxisKey} fill="#6366f1" radius={[6, 6, 0, 0]} name={yAxisKey.replace('_', ' ').toUpperCase()} />
                </BarChart>
              ) : chartType === 'line' ? (
                <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis 
                    dataKey={xAxisKey} 
                    stroke="#64748b" 
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    angle={-35} 
                    textAnchor="end" 
                    interval={0}
                  />
                  <YAxis 
                    stroke="#64748b" 
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    tickFormatter={(val) => val >= 1000 ? `${(val / 1000).toFixed(1)}k` : val}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                    formatter={(val) => [typeof val === 'number' ? val.toLocaleString() : val, yAxisKey]}
                  />
                  <Legend wrapperStyle={{ paddingTop: '20px', fontSize: '12px' }} />
                  <Line type="monotone" dataKey={yAxisKey} stroke="#06b6d4" strokeWidth={3} dot={{ r: 4, fill: '#06b6d4' }} activeDot={{ r: 6 }} name={yAxisKey.replace('_', ' ').toUpperCase()} />
                </LineChart>
              ) : chartType === 'area' ? (
                <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                  <defs>
                    <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis 
                    dataKey={xAxisKey} 
                    stroke="#64748b" 
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    angle={-35} 
                    textAnchor="end" 
                    interval={0}
                  />
                  <YAxis 
                    stroke="#64748b" 
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    tickFormatter={(val) => val >= 1000 ? `${(val / 1000).toFixed(1)}k` : val}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                    formatter={(val) => [typeof val === 'number' ? val.toLocaleString() : val, yAxisKey]}
                  />
                  <Legend wrapperStyle={{ paddingTop: '20px', fontSize: '12px' }} />
                  <Area type="monotone" dataKey={yAxisKey} stroke="#6366f1" strokeWidth={2} fillOpacity={1} fill="url(#areaGradient)" name={yAxisKey.replace('_', ' ').toUpperCase()} />
                </AreaChart>
              ) : (
                <PieChart>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                    formatter={(val) => [typeof val === 'number' ? val.toLocaleString() : val, yAxisKey]}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Pie
                    data={chartData}
                    dataKey={yAxisKey}
                    nameKey={xAxisKey}
                    cx="50%"
                    cy="50%"
                    outerRadius={130}
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                    labelLine={false}
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                </PieChart>
              )}
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
