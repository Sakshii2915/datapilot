import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import QueryAssistant from './components/QueryAssistant';
import ResultsExplorer from './components/ResultsExplorer';
import VisualAnalytics from './components/VisualAnalytics';
import SchemaExplorer from './components/SchemaExplorer';
import QueryHistoryView from './components/QueryHistoryView';
import DashboardOverview from './pages/DashboardOverview';
import { apiService } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [health, setHealth] = useState(null);
  const [schema, setSchema] = useState(null);
  const [queryResult, setQueryResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Initial Data Fetch
  useEffect(() => {
    fetchHealth();
    fetchSchema();
    fetchHistory();
  }, []);

  const fetchHealth = async () => {
    try {
      const data = await apiService.getHealth();
      setHealth(data);
    } catch (err) {
      console.error('Failed to fetch system health:', err);
    }
  };

  const fetchSchema = async () => {
    try {
      const data = await apiService.getSchema();
      setSchema(data);
    } catch (err) {
      console.error('Failed to fetch schema:', err);
    }
  };

  const fetchHistory = async () => {
    try {
      const data = await apiService.getHistory(30);
      setHistory(data);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    }
  };

  const handleRefreshSchema = async () => {
    setIsRefreshing(true);
    try {
      await apiService.refreshSchema();
      await fetchSchema();
    } catch (err) {
      console.error('Failed to refresh schema:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleSubmitQuery = async (question) => {
    setIsLoading(true);
    setActiveTab('assistant');
    try {
      const result = await apiService.submitQuery(question);
      setQueryResult(result);
      fetchHistory();
    } catch (err) {
      console.error('Query execution error:', err);
      setQueryResult({
        question,
        execution_status: 'error',
        error_message: err.response?.data?.detail || err.message || 'An unexpected network error occurred.',
        is_mock: false,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteHistoryItem = async (id) => {
    try {
      await apiService.deleteHistoryItem(id);
      setHistory((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      console.error('Failed to delete history item:', err);
    }
  };

  const handleClearAllHistory = async () => {
    try {
      await apiService.clearAllHistory();
      setHistory([]);
    } catch (err) {
      console.error('Failed to clear history:', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navigation */}
      <Navbar
        health={health}
        onRefreshSchema={handleRefreshSchema}
        isRefreshing={isRefreshing}
      />

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          historyCount={history.length}
        />

        {/* Viewport Content */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-slate-950">
          {activeTab === 'dashboard' && (
            <DashboardOverview
              onSelectPrompt={handleSubmitQuery}
              onNavigateTab={setActiveTab}
              history={history}
            />
          )}

          {activeTab === 'assistant' && (
            <QueryAssistant
              queryResult={queryResult}
              isLoading={isLoading}
              onSubmitQuery={handleSubmitQuery}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'explorer' && (
            <ResultsExplorer queryResult={queryResult} />
          )}

          {activeTab === 'analytics' && (
            <VisualAnalytics queryResult={queryResult} />
          )}

          {activeTab === 'schema' && (
            <SchemaExplorer
              schema={schema}
              onRefreshSchema={handleRefreshSchema}
              isRefreshing={isRefreshing}
            />
          )}

          {activeTab === 'history' && (
            <QueryHistoryView
              history={history}
              onRunQuestion={handleSubmitQuery}
              onDeleteHistoryItem={handleDeleteHistoryItem}
              onClearAllHistory={handleClearAllHistory}
            />
          )}
        </main>
      </div>
    </div>
  );
}
