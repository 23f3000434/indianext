import { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion, useInView } from 'framer-motion';
import GlassCard from '../components/shared/GlassCard';
import RiskGauge from '../components/shared/RiskGauge';
import SeverityBadge from '../components/shared/SeverityBadge';
import useStore from '../store/useStore';
import { getThreatFeed } from '../services/api';

/* ──────────────────────────────────────────────
   Animation Variants
   ────────────────────────────────────────────── */
const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] },
  },
};

const cardHover = {
  scale: 1.015,
  transition: { duration: 0.25, ease: 'easeOut' },
};

/* ──────────────────────────────────────────────
   Animated Counter Hook
   ────────────────────────────────────────────── */
function useAnimatedCounter(target, duration = 1400) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (!isInView) return;
    const numericTarget = typeof target === 'number' ? target : 0;
    if (numericTarget === 0) {
      setCount(0);
      return;
    }
    let start = 0;
    const startTime = performance.now();
    function tick(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      start = Math.round(eased * numericTarget);
      setCount(start);
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }, [isInView, target, duration]);

  return { count, ref };
}

/* ──────────────────────────────────────────────
   Inline SVG Icons
   ────────────────────────────────────────────── */
const icons = {
  barChart: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="12" width="4" height="9" rx="1" />
      <rect x="10" y="7" width="4" height="14" rx="1" />
      <rect x="17" y="3" width="4" height="18" rx="1" />
    </svg>
  ),
  alertTriangle: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  ),
  shieldCheck: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      <polyline points="9 12 11 14 15 10" />
    </svg>
  ),
  cpu: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="4" width="16" height="16" rx="2" />
      <rect x="9" y="9" width="6" height="6" rx="1" />
      <line x1="9" y1="1" x2="9" y2="4" /><line x1="15" y1="1" x2="15" y2="4" />
      <line x1="9" y1="20" x2="9" y2="23" /><line x1="15" y1="20" x2="15" y2="23" />
      <line x1="20" y1="9" x2="23" y2="9" /><line x1="20" y1="15" x2="23" y2="15" />
      <line x1="1" y1="9" x2="4" y2="9" /><line x1="1" y1="15" x2="4" y2="15" />
    </svg>
  ),
  mail: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <polyline points="22,6 12,13 2,6" />
    </svg>
  ),
  link: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" />
      <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" />
    </svg>
  ),
  video: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="23 7 16 12 23 17 23 7" />
      <rect x="1" y="5" width="15" height="14" rx="2" />
    </svg>
  ),
  terminal: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="4 17 10 11 4 5" />
      <line x1="12" y1="19" x2="20" y2="19" />
    </svg>
  ),
  activity: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  ),
  bot: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="8" width="18" height="12" rx="2" />
      <circle cx="9" cy="14" r="1.5" />
      <circle cx="15" cy="14" r="1.5" />
      <line x1="12" y1="4" x2="12" y2="8" />
      <circle cx="12" cy="3" r="1" />
    </svg>
  ),
  arrowRight: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </svg>
  ),
  clock: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  ),
};

/* ──────────────────────────────────────────────
   Threat Modules Data
   ────────────────────────────────────────────── */
const threatModules = [
  {
    title: 'Phishing Email',
    description: 'Detect social engineering, spoofed headers, and malicious payloads in emails.',
    icon: icons.mail,
    color: 'var(--purple-primary)',
    link: '/analyze',
  },
  {
    title: 'Malicious URL',
    description: 'Analyze URLs for phishing domains, drive-by downloads, and C2 endpoints.',
    icon: icons.link,
    color: 'var(--cyan-primary)',
    link: '/analyze',
  },
  {
    title: 'Deepfake Detection',
    description: 'AI-powered analysis to identify manipulated media and synthetic content.',
    icon: icons.video,
    color: 'var(--red-primary)',
    link: '/analyze',
  },
  {
    title: 'Prompt Injection',
    description: 'Identify adversarial prompt attacks targeting LLMs and AI systems.',
    icon: icons.terminal,
    color: 'var(--yellow-primary)',
    link: '/analyze',
  },
  {
    title: 'Behavior Anomaly',
    description: 'Detect suspicious behavioral patterns and lateral movement indicators.',
    icon: icons.activity,
    color: 'var(--green-primary)',
    link: '/analyze',
  },
  {
    title: 'AI Content Detection',
    description: 'Determine if text was generated by an AI model with confidence scoring.',
    icon: icons.bot,
    color: 'var(--cyan-primary)',
    link: '/analyze',
  },
];

/* ──────────────────────────────────────────────
   Helper: risk score -> severity key
   ────────────────────────────────────────────── */
function scoreSeverity(score) {
  if (score <= 20) return 'safe';
  if (score <= 40) return 'low';
  if (score <= 60) return 'medium';
  if (score <= 80) return 'high';
  return 'critical';
}

/* ──────────────────────────────────────────────
   Helper: format timestamp
   ────────────────────────────────────────────── */
function formatTimestamp(ts) {
  if (!ts) return '';
  const date = new Date(ts);
  const now = new Date();
  const diff = (now - date) / 1000;
  if (diff < 60) return 'Just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

/* ──────────────────────────────────────────────
   Helper: threat type icon
   ────────────────────────────────────────────── */
function threatTypeIcon(type) {
  const map = {
    phishing: icons.mail,
    malicious_url: icons.link,
    deepfake: icons.video,
    prompt_injection: icons.terminal,
    anomalous_behavior: icons.activity,
    ai_generated_content: icons.bot,
  };
  return map[type] || icons.alertTriangle;
}

/* ══════════════════════════════════════════════
   Dashboard Component
   ══════════════════════════════════════════════ */
function Dashboard() {
  const { totalAnalyzed, threatsDetected } = useStore();
  const [recentThreats, setRecentThreats] = useState([]);
  const [threatLoading, setThreatLoading] = useState(true);

  const safetyRate = totalAnalyzed > 0
    ? ((totalAnalyzed - threatsDetected) / totalAnalyzed) * 100
    : 100;

  // Animated counters
  const totalCounter = useAnimatedCounter(totalAnalyzed);
  const threatsCounter = useAnimatedCounter(threatsDetected);
  const safetyCounter = useAnimatedCounter(Math.round(safetyRate));

  // Fetch recent threats on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await getThreatFeed();
        if (!cancelled) {
          const threats = res.data?.threats ?? res.data ?? [];
          setRecentThreats(Array.isArray(threats) ? threats.slice(0, 5) : []);
        }
      } catch {
        // silently fail -- no threats yet is fine
      } finally {
        if (!cancelled) setThreatLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  /* ── Render ────────────────────────────────── */
  return (
    <div className="relative z-10 px-4 py-8 sm:px-6 lg:px-8 xl:px-10 2xl:px-12">
      <motion.div
        className="mx-auto w-full max-w-[1680px]"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* ── Hero Section ─────────────────────── */}
        <motion.header variants={itemVariants} className="mb-12 text-center lg:text-left">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-none mb-2">
            <span className="text-[var(--text-primary)]">Threat Intelligence</span>
            <br />
            <span className="gradient-text">Dashboard</span>
          </h1>
          <p className="mt-4 text-base sm:text-lg text-[var(--text-secondary)] max-w-2xl lg:max-w-none">
            Real-time AI-powered cyber threat detection and analysis
          </p>
        </motion.header>

        {/* ── Stats Row ────────────────────────── */}
        <motion.div
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-10"
          variants={containerVariants}
        >
          {/* Total Analyzed */}
          <motion.div variants={itemVariants} whileHover={cardHover}>
            <GlassCard className="relative overflow-hidden">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
                  Total Analyzed
                </span>
                <span className="text-[var(--purple-primary)] opacity-70">{icons.barChart}</span>
              </div>
              <p
                ref={totalCounter.ref}
                className="text-4xl font-bold tabular-nums"
                style={{ color: 'var(--purple-primary)' }}
              >
                {totalCounter.count.toLocaleString()}
              </p>
              {/* accent line */}
              <div className="absolute bottom-0 left-0 right-0 h-[2px]" style={{ background: 'linear-gradient(90deg, var(--purple-primary), transparent)' }} />
            </GlassCard>
          </motion.div>

          {/* Threats Detected */}
          <motion.div variants={itemVariants} whileHover={cardHover}>
            <GlassCard className="relative overflow-hidden">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
                  Threats Detected
                </span>
                <span className="text-[var(--red-primary)] opacity-70">{icons.alertTriangle}</span>
              </div>
              <p
                ref={threatsCounter.ref}
                className="text-4xl font-bold tabular-nums"
                style={{ color: 'var(--red-primary)' }}
              >
                {threatsCounter.count.toLocaleString()}
              </p>
              <div className="absolute bottom-0 left-0 right-0 h-[2px]" style={{ background: 'linear-gradient(90deg, var(--red-primary), transparent)' }} />
            </GlassCard>
          </motion.div>

          {/* Safety Rate */}
          <motion.div variants={itemVariants} whileHover={cardHover}>
            <GlassCard className="relative overflow-hidden">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
                  Safety Rate
                </span>
                <span className="text-[var(--green-primary)] opacity-70">{icons.shieldCheck}</span>
              </div>
              <p
                ref={safetyCounter.ref}
                className="text-4xl font-bold tabular-nums"
                style={{ color: 'var(--green-primary)' }}
              >
                {totalAnalyzed > 0 ? `${safetyCounter.count}%` : '--'}
              </p>
              <div className="absolute bottom-0 left-0 right-0 h-[2px]" style={{ background: 'linear-gradient(90deg, var(--green-primary), transparent)' }} />
            </GlassCard>
          </motion.div>

          {/* Active Modules */}
          <motion.div variants={itemVariants} whileHover={cardHover}>
            <GlassCard className="relative overflow-hidden">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
                  Active Modules
                </span>
                <span className="text-[var(--cyan-primary)] opacity-70">{icons.cpu}</span>
              </div>
              <p className="text-4xl font-bold tabular-nums" style={{ color: 'var(--cyan-primary)' }}>
                6
              </p>
              <div className="absolute bottom-0 left-0 right-0 h-[2px]" style={{ background: 'linear-gradient(90deg, var(--cyan-primary), transparent)' }} />
            </GlassCard>
          </motion.div>
        </motion.div>

        {/* ── Quick Actions ────────────────────── */}
        <motion.div
          className="flex flex-wrap items-center gap-4 mb-12"
          variants={itemVariants}
        >
          <Link to="/analyze">
            <motion.button
              whileHover={{ scale: 1.04, boxShadow: '0 0 30px rgba(168,130,255,0.35)' }}
              whileTap={{ scale: 0.97 }}
              className="px-8 py-3.5 rounded-xl font-semibold text-white text-sm tracking-wide
                         bg-gradient-to-r from-[var(--purple-primary)] to-[var(--purple-dark)]
                         shadow-lg shadow-purple-500/20 transition-colors cursor-pointer"
            >
              Start Analysis
            </motion.button>
          </Link>

          <Link to="/threat-feed">
            <motion.button
              whileHover={{ scale: 1.04, borderColor: 'rgba(168,130,255,0.4)' }}
              whileTap={{ scale: 0.97 }}
              className="glass-chip px-6 py-3.5 rounded-xl font-semibold text-[var(--text-secondary)] text-sm tracking-wide
                         hover:text-[var(--text-primary)] transition-all cursor-pointer"
            >
              View Threat Feed
            </motion.button>
          </Link>

          <Link to="/adversarial">
            <motion.button
              whileHover={{ scale: 1.04, borderColor: 'rgba(168,130,255,0.4)' }}
              whileTap={{ scale: 0.97 }}
              className="glass-chip px-6 py-3.5 rounded-xl font-semibold text-[var(--text-secondary)] text-sm tracking-wide
                         hover:text-[var(--text-primary)] transition-all cursor-pointer"
            >
              Adversarial Testing
            </motion.button>
          </Link>
        </motion.div>

        {/* ── Threat Modules Grid ──────────────── */}
        <motion.div variants={itemVariants} className="mb-12">
          <h2 className="text-xl font-bold text-[var(--text-primary)] mb-6 tracking-tight">
            Threat Analysis Modules
          </h2>

          <motion.div
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5"
            variants={containerVariants}
          >
            {threatModules.map((mod) => (
              <motion.div key={mod.title} variants={itemVariants}>
                <Link to={mod.link} className="block h-full">
                  <motion.div
                    whileHover={{
                      scale: 1.02,
                      borderColor: 'rgba(168,130,255,0.35)',
                      boxShadow: '0 0 24px rgba(168,130,255,0.1), 0 8px 32px rgba(0,0,0,0.3)',
                    }}
                    className="glass-card h-full rounded-2xl p-6
                               transition-all duration-300 group"
                  >
                    {/* Icon */}
                    <div
                      className="w-12 h-12 rounded-xl flex items-center justify-center mb-4
                                 transition-transform duration-300 group-hover:scale-110"
                      style={{
                        background: `${mod.color}15`,
                        color: mod.color,
                      }}
                    >
                      {mod.icon}
                    </div>

                    <h3 className="text-base font-semibold text-[var(--text-primary)] mb-1.5 tracking-tight">
                      {mod.title}
                    </h3>

                    <p className="text-xs text-[var(--text-secondary)] leading-relaxed mb-4">
                      {mod.description}
                    </p>

                    <span
                      className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider
                                 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                      style={{ color: mod.color }}
                    >
                      Analyze {icons.arrowRight}
                    </span>
                  </motion.div>
                </Link>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* ── Recent Threats ────────────────────── */}
        <motion.div variants={itemVariants}>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-[var(--text-primary)] tracking-tight">
              Recent Threat Activity
            </h2>
            <Link
              to="/threat-feed"
              className="text-xs font-semibold text-[var(--purple-primary)] hover:text-[var(--purple-light)]
                         uppercase tracking-wider transition-colors inline-flex items-center gap-1"
            >
              View All {icons.arrowRight}
            </Link>
          </div>

          <GlassCard padding="p-0" hover={false}>
            {threatLoading ? (
              /* Loading skeleton */
              <div className="p-8 flex flex-col gap-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="glass-card-soft h-12 rounded-lg animate-shimmer" />
                ))}
              </div>
            ) : recentThreats.length === 0 ? (
              /* Empty state */
              <div className="p-12 text-center">
                <div className="glass-card-soft w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center text-[var(--text-muted)]">
                  {icons.shieldCheck}
                </div>
                <p className="text-sm text-[var(--text-secondary)] mb-1">
                  No threats analyzed yet.
                </p>
                <p className="text-xs text-[var(--text-muted)]">
                  <Link to="/analyze" className="text-[var(--purple-primary)] hover:underline">
                    Start your first analysis
                  </Link>{' '}
                  to populate threat data.
                </p>
              </div>
            ) : (
              /* Threat rows */
              <div className="divide-y divide-white/[0.04]">
                {recentThreats.map((threat, idx) => (
                  <motion.div
                    key={threat.id || idx}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.06, duration: 0.35 }}
                    className="flex items-center gap-4 px-6 py-4 hover:bg-[rgba(22,18,36,0.34)] transition-colors"
                  >
                    {/* Type icon */}
                    <div className="glass-card-soft w-9 h-9 rounded-lg flex items-center justify-center text-[var(--text-muted)] shrink-0">
                      <span className="scale-[0.65]">
                        {threatTypeIcon(threat.threat_type)}
                      </span>
                    </div>

                    {/* Summary */}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-[var(--text-primary)] truncate">
                        {threat.explanation?.summary || threat.threat_type || 'Unknown threat'}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5 text-[var(--text-muted)]">
                        {icons.clock}
                        <span className="text-[10px]">{formatTimestamp(threat.timestamp || threat.created_at)}</span>
                      </div>
                    </div>

                    {/* Severity badge */}
                    <div className="shrink-0">
                      <SeverityBadge
                        severity={threat.severity || scoreSeverity(threat.risk_score ?? 0)}
                        size="sm"
                      />
                    </div>

                    {/* Risk score */}
                    <div className="shrink-0 w-12 text-right">
                      <span className="text-sm font-bold tabular-nums" style={{
                        color: threat.risk_score > 60 ? 'var(--red-primary)'
                          : threat.risk_score > 30 ? 'var(--yellow-primary)'
                            : 'var(--green-primary)'
                      }}>
                        {threat.risk_score ?? '--'}
                      </span>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </GlassCard>
        </motion.div>

        {/* ── Bottom Spacer ────────────────────── */}
        <div className="h-8" />
      </motion.div>
    </div>
  );
}

export default Dashboard;
