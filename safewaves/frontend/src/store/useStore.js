import { create } from 'zustand';

const useStore = create((set, get) => ({
  // ── Current Analysis State ───────────────────────
  currentAnalysis: null,
  isAnalyzing: false,
  error: null,

  // ── Threat Feed ──────────────────────────────────
  threatFeed: [],

  // ── Aggregate Stats ──────────────────────────────
  totalAnalyzed: 0,
  threatsDetected: 0,

  // ── SSE Connection ───────────────────────────────
  sseConnected: false,

  // ── Fusion Result ────────────────────────────────
  fusionResult: null,

  // ── Actions ──────────────────────────────────────
  setAnalyzing: (isAnalyzing) => set({ isAnalyzing, error: null }),

  setCurrentAnalysis: (analysis) =>
    set({
      currentAnalysis: analysis,
      isAnalyzing: false,
      totalAnalyzed: get().totalAnalyzed + 1,
      threatsDetected: analysis?.is_threat
        ? get().threatsDetected + 1
        : get().threatsDetected,
    }),

  setError: (error) => set({ error, isAnalyzing: false }),

  setThreatFeed: (threats) => set({ threatFeed: threats }),

  addThreatFromSSE: (threat) =>
    set((state) => ({
      threatFeed: [threat, ...state.threatFeed].slice(0, 100),
      totalAnalyzed: state.totalAnalyzed + 1,
      threatsDetected: threat.is_threat
        ? state.threatsDetected + 1
        : state.threatsDetected,
    })),

  setSseConnected: (connected) => set({ sseConnected: connected }),

  setFusionResult: (result) => set({ fusionResult: result }),

  clearAnalysis: () => set({ currentAnalysis: null, error: null }),

  setStats: (stats) =>
    set({
      totalAnalyzed: stats.total_analyzed || 0,
      threatsDetected: stats.threats_detected || 0,
    }),
}));

export default useStore;
