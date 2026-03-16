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

  clearAnalysis: () => set({ currentAnalysis: null, error: null }),
}));

export default useStore;
