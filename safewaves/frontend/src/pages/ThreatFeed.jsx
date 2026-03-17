import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import GlassCard from '../components/shared/GlassCard';
import SeverityBadge from '../components/shared/SeverityBadge';
import { getThreatFeed, createThreatStream } from '../services/api';

/* ── Inline SVG Icons per threat type ──────────────────────── */
const THREAT_ICONS = {
  phishing: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
      <polyline points="22,6 12,13 2,6" />
    </svg>
  ),
  malicious_url: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
    </svg>
  ),
  deepfake: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
      <circle cx="12" cy="13" r="4" />
    </svg>
  ),
  prompt_injection: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="4 17 10 11 4 5" />
      <line x1="12" y1="19" x2="20" y2="19" />
    </svg>
  ),
  anomalous_behavior: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </svg>
  ),
  ai_generated_content: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <path d="M12 16v-4" />
      <path d="M12 8h.01" />
      <path d="M8 12h8" />
      <path d="M12 8v-4" />
    </svg>
  ),
};

const THREAT_TYPE_LABELS = {
  phishing: 'Phishing',
  malicious_url: 'URL',
  deepfake: 'Deepfake',
  prompt_injection: 'Prompt',
  anomalous_behavior: 'Behavior',
  ai_generated_content: 'AI Content',
};

const TYPE_FILTERS = ['all', 'phishing', 'malicious_url', 'deepfake', 'prompt_injection', 'anomalous_behavior', 'ai_generated_content'];
const SEVERITY_FILTERS = ['all', 'critical', 'high', 'medium', 'low', 'safe'];

/* ── Helpers ───────────────────────────────────────────────── */
function relativeTime(timestamp) {
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);
  if (diffSec < 60) return `${diffSec}s ago`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay}d ago`;
}

function scoreColor(score) {
  if (score <= 20) return 'text-green-400';
  if (score <= 40) return 'text-yellow-400';
  if (score <= 60) return 'text-amber-400';
  if (score <= 80) return 'text-orange-400';
  return 'text-red-400';
}

/* ── Shimmer Skeleton ──────────────────────────────────────── */
function SkeletonRow() {
  return (
    <div className="glass-card rounded-2xl p-5 animate-pulse">
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-xl bg-white/[0.06]" />
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-white/[0.06] rounded w-3/4" />
          <div className="h-3 rounded w-1/2 bg-[rgba(22,18,36,0.52)]" />
        </div>
        <div className="w-16 h-6 bg-white/[0.06] rounded-full" />
        <div className="w-10 h-5 bg-white/[0.06] rounded" />
      </div>
    </div>
  );
}

/* ── Confidence Meter ──────────────────────────────────────── */
function ConfidenceMeter({ value = 0 }) {
  const pct = Math.max(0, Math.min(100, Math.round(value * 100)));
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-[var(--text-muted)]">
        <span>Confidence</span>
        <span className="text-purple-300 font-semibold">{pct}%</span>
      </div>
      <div className="h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full bg-gradient-to-r from-purple-500 to-indigo-500"
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}

/* ── Expandable Threat Card ────────────────────────────────── */
function ThreatCard({ threat, index }) {
  const [expanded, setExpanded] = useState(false);

  const icon = THREAT_ICONS[threat.threat_type] || THREAT_ICONS.behavior;
  const typeLabel = THREAT_TYPE_LABELS[threat.threat_type] || threat.threat_type;
  const severityKey = (threat.severity || 'safe').toLowerCase();

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12, scale: 0.97 }}
      transition={{ duration: 0.35, delay: index * 0.04, ease: [0.25, 0.46, 0.45, 0.94] }}
    >
      <div
        className={[
          'glass-card rounded-2xl overflow-hidden transition-all duration-300 cursor-pointer select-none',
          expanded
            ? 'border-purple-500/30 shadow-lg shadow-purple-500/5'
            : 'border-white/[0.06] hover:border-purple-400/20 hover:shadow-md hover:shadow-purple-500/5',
        ].join(' ')}
        onClick={() => setExpanded((prev) => !prev)}
      >
        {/* Collapsed row */}
        <div className="flex items-center gap-4 px-5 py-4">
          {/* Icon */}
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 shrink-0">
            {icon}
          </div>

          {/* Type label */}
          <span className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)] w-20 shrink-0">
            {typeLabel}
          </span>

          {/* Severity badge */}
          <div className="shrink-0">
            <SeverityBadge severity={severityKey} size="sm" />
          </div>

          {/* Risk score */}
          <span className={`text-lg font-bold tabular-nums shrink-0 ${scoreColor(threat.risk_score)}`}>
            {threat.risk_score}
          </span>

          {/* Summary */}
          <p className="flex-1 text-sm text-[var(--text-secondary)] truncate min-w-0">
            {threat.explanation?.summary || 'No summary available'}
          </p>

          {/* Timestamp */}
          <span className="text-xs text-[var(--text-muted)] whitespace-nowrap shrink-0">
            {threat.timestamp ? relativeTime(threat.timestamp) : '--'}
          </span>

          {/* Expand chevron */}
          <motion.svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-[var(--text-muted)] shrink-0"
            animate={{ rotate: expanded ? 180 : 0 }}
            transition={{ duration: 0.25 }}
          >
            <polyline points="6 9 12 15 18 9" />
          </motion.svg>
        </div>

        {/* Expanded details */}
        <AnimatePresence initial={false}>
          {expanded && (
            <motion.div
              key="details"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
              className="overflow-hidden"
            >
              <div className="px-5 pb-5 pt-1 border-t border-white/[0.04] space-y-4">
                {/* Full explanation */}
                {threat.explanation?.summary && (
                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)] mb-1.5">
                      Explanation
                    </h4>
                    <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                      {threat.explanation.summary}
                    </p>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Key factors */}
                  {threat.explanation?.key_factors && threat.explanation.key_factors.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)] mb-2">
                        Key Factors
                      </h4>
                      <ul className="space-y-1.5">
                        {threat.explanation.key_factors.map((factor, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                            <svg
                              width="14"
                              height="14"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="#a882ff"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              className="mt-0.5 shrink-0"
                            >
                              <path d="M9 18l6-6-6-6" />
                            </svg>
                            <span>
                              <span className="font-medium text-purple-300">{factor.feature}</span>
                              {factor.value !== undefined && <span className="text-[var(--text-muted)]"> = {String(factor.value)}</span>}
                              {factor.description && <span className="text-[var(--text-muted)]"> — {factor.description}</span>}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Recommendations */}
                  {threat.recommendations && threat.recommendations.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)] mb-2">
                        Recommendations
                      </h4>
                      <ul className="space-y-1.5">
                        {threat.recommendations.map((rec, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                            <svg
                              width="14"
                              height="14"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="#22c55e"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              className="mt-0.5 shrink-0"
                            >
                              <polyline points="20 6 9 17 4 12" />
                            </svg>
                            <span>
                              <span className="font-medium">{rec.action || rec}</span>
                              {rec.description && <span className="text-[var(--text-muted)]"> — {rec.description}</span>}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Confidence meter */}
                {threat.confidence !== undefined && (
                  <div className="max-w-xs">
                    <ConfidenceMeter value={threat.confidence} />
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

/* ── Main Page ─────────────────────────────────────────────── */
function ThreatFeed() {
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [typeFilter, setTypeFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [sseConnected, setSseConnected] = useState(false);
  const eventSourceRef = useRef(null);

  /* Fetch threats (initial load + fallback) */
  const fetchThreats = useCallback(async () => {
    try {
      const res = await getThreatFeed();
      setThreats(res.data?.threats ?? res.data ?? []);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load threat feed');
    } finally {
      setLoading(false);
    }
  }, []);

  /* SSE real-time stream with polling fallback */
  useEffect(() => {
    fetchThreats();

    // Try SSE connection
    let es;
    try {
      es = createThreatStream();
      eventSourceRef.current = es;

      es.addEventListener('connected', () => {
        setSseConnected(true);
      });

      es.addEventListener('threat', (event) => {
        try {
          const newThreat = JSON.parse(event.data);
          setThreats((prev) => [newThreat, ...prev].slice(0, 100));
        } catch { /* ignore parse errors */ }
      });

      es.onerror = () => {
        setSseConnected(false);
      };
    } catch {
      // SSE not available, fall through to polling
    }

    // Polling fallback (less frequent when SSE is active)
    const interval = setInterval(fetchThreats, sseConnected ? 30000 : 10000);

    return () => {
      clearInterval(interval);
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, []);

  /* Filtered list */
  const filtered = threats.filter((t) => {
    const matchType = typeFilter === 'all' || t.threat_type === typeFilter;
    const matchSev = severityFilter === 'all' || (t.severity || '').toLowerCase() === severityFilter;
    return matchType && matchSev;
  });

  return (
    <div className="mx-auto w-full max-w-[1600px] space-y-8 animate-fade-in p-6 md:p-8 xl:px-10 2xl:px-12">
      {/* ── Header ─────────────────────────────────────────── */}
      <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1">
            <span className="gradient-text">Threat Feed</span>
          </h1>
          <p className="text-[var(--text-secondary)] text-sm">
            Real-time log of all analyzed threats
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Live indicator */}
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${sseConnected
              ? 'bg-green-500/10 border-green-500/20'
              : 'bg-yellow-500/10 border-yellow-500/20'
            }`}>
            <span className="relative flex h-2 w-2">
              <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping ${sseConnected ? 'bg-green-400' : 'bg-yellow-400'
                }`} />
              <span className={`relative inline-flex rounded-full h-2 w-2 ${sseConnected ? 'bg-green-500' : 'bg-yellow-500'
                }`} />
            </span>
            <span className={`text-xs font-semibold uppercase tracking-wider ${sseConnected ? 'text-green-400' : 'text-yellow-400'
              }`}>{sseConnected ? 'Live SSE' : 'Polling'}</span>
          </div>

          {/* Total count */}
          {!loading && (
            <motion.span
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="px-3 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-xs font-semibold text-purple-300 tabular-nums"
            >
              {threats.length} total
            </motion.span>
          )}
        </div>
      </header>

      {/* ── Filters ────────────────────────────────────────── */}
      <GlassCard hover={false} padding="p-4">
        <div className="space-y-3">
          {/* Type filters */}
          <div className="space-y-1.5">
            <span className="text-[10px] font-semibold uppercase tracking-widest text-[var(--text-muted)]">
              Threat Type
            </span>
            <div className="flex flex-wrap gap-2">
              {TYPE_FILTERS.map((f) => (
                <button
                  key={f}
                  onClick={() => setTypeFilter(f)}
                  className={[
                    'px-3 py-1.5 rounded-lg text-xs font-semibold capitalize tracking-wide transition-all duration-200 cursor-pointer',
                    typeFilter === f
                      ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-sm shadow-purple-500/10'
                      : 'glass-chip text-[var(--text-muted)] hover:bg-[rgba(22,18,36,0.62)] hover:text-[var(--text-secondary)]',
                  ].join(' ')}
                >
                  {THREAT_TYPE_LABELS[f] || f}
                </button>
              ))}
            </div>
          </div>

          {/* Severity filters */}
          <div className="space-y-1.5">
            <span className="text-[10px] font-semibold uppercase tracking-widest text-[var(--text-muted)]">
              Severity
            </span>
            <div className="flex flex-wrap gap-2">
              {SEVERITY_FILTERS.map((f) => (
                <button
                  key={f}
                  onClick={() => setSeverityFilter(f)}
                  className={[
                    'px-3 py-1.5 rounded-lg text-xs font-semibold capitalize tracking-wide transition-all duration-200 cursor-pointer',
                    severityFilter === f
                      ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-sm shadow-purple-500/10'
                      : 'glass-chip text-[var(--text-muted)] hover:bg-[rgba(22,18,36,0.62)] hover:text-[var(--text-secondary)]',
                  ].join(' ')}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
        </div>
      </GlassCard>

      {/* ── Error Banner ───────────────────────────────────── */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 px-5 py-3 rounded-xl bg-red-500/10 border border-red-500/20"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
          <span className="text-sm text-red-400">{error}</span>
        </motion.div>
      )}

      {/* ── Loading Skeleton ───────────────────────────────── */}
      {loading && (
        <div className="space-y-3">
          <SkeletonRow />
          <SkeletonRow />
          <SkeletonRow />
        </div>
      )}

      {/* ── Threat List ────────────────────────────────────── */}
      {!loading && filtered.length > 0 && (
        <div className="space-y-3">
          <AnimatePresence mode="popLayout">
            {filtered.map((threat, idx) => (
              <ThreatCard
                key={threat.id || `${threat.threat_type}-${threat.timestamp}-${idx}`}
                threat={threat}
                index={idx}
              />
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* ── Empty State ────────────────────────────────────── */}
      {!loading && threats.length === 0 && !error && (
        <GlassCard hover={false} padding="p-10">
          <div className="flex flex-col items-center text-center space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-purple-500/10 flex items-center justify-center">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#a882ff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-1">
                No threats analyzed yet
              </h3>
              <p className="text-sm text-[var(--text-muted)] max-w-sm">
                Start analyzing emails, URLs, or content to see threats appear in this feed.
              </p>
            </div>
            <Link
              to="/analyze"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-sm font-semibold shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40 transition-all duration-300 hover:scale-[1.03] active:scale-[0.97]"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
              Go to Analyze
            </Link>
          </div>
        </GlassCard>
      )}

      {/* ── Filtered empty state ───────────────────────────── */}
      {!loading && threats.length > 0 && filtered.length === 0 && (
        <GlassCard hover={false} padding="p-8">
          <div className="flex flex-col items-center text-center space-y-3">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#a882ff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="opacity-50">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <p className="text-sm text-[var(--text-muted)]">
              No threats match the current filters. Try adjusting your selection.
            </p>
          </div>
        </GlassCard>
      )}
    </div>
  );
}

export default ThreatFeed;
