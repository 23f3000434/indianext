import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Request Interceptor ────────────────────────────
api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

// ── Response Interceptor ───────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';

    console.error('[API Error]', message);
    return Promise.reject(error);
  }
);

// ── Analysis Endpoints ─────────────────────────────
export const analyzeEmail = (data) => api.post('/analyze/email', data);

export const analyzeUrl = (data) => api.post('/analyze/url', data);

export const analyzeDeepfake = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/analyze/deepfake', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const analyzePrompt = (data) => api.post('/analyze/prompt', data);

export const analyzeBehavior = (data) => api.post('/analyze/behavior', data);

export const analyzeAiContent = (data) => api.post('/analyze/ai-content', data);

// ── Threat Feed ────────────────────────────────────
export const getThreatFeed = () => api.get('/threat-feed');

// ── Adversarial Testing ────────────────────────────
export const runAdversarialTest = (data) => api.post('/adversarial-test', data);

export default api;
