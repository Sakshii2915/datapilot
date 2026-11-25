import axios from 'axios';

const API_BASE = '/api';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const apiService = {
  // Health
  getHealth: async () => {
    const res = await client.get('/health');
    return res.data;
  },

  // Schema
  getSchema: async () => {
    const res = await client.get('/schema');
    return res.data;
  },

  getTableSchema: async (tableName) => {
    const res = await client.get(`/schema/tables/${tableName}`);
    return res.data;
  },

  refreshSchema: async () => {
    const res = await client.post('/schema/refresh');
    return res.data;
  },

  // Query Engine
  submitQuery: async (question) => {
    const res = await client.post('/query', { question });
    return res.data;
  },

  validateSQL: async (sql) => {
    const res = await client.post('/query/validate', { sql });
    return res.data;
  },

  // History
  getHistory: async (limit = 25, offset = 0, status = null) => {
    const params = { limit, offset };
    if (status) params.status = status;
    const res = await client.get('/query/history', { params });
    return res.data;
  },

  getHistoryDetail: async (queryId) => {
    const res = await client.get(`/query/history/${queryId}`);
    return res.data;
  },

  deleteHistoryItem: async (queryId) => {
    const res = await client.delete(`/query/history/${queryId}`);
    return res.data;
  },

  clearAllHistory: async () => {
    const res = await client.delete('/query/history');
    return res.data;
  },
};
