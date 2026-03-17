import { useMemo } from 'react';
import { motion } from 'framer-motion';
import GlassCard from '../shared/GlassCard';

/** Inline SVG shield icon. */
function ShieldIcon({ size = 18, color = '#a882ff' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}

/** Inline SVG warning triangle icon. */
function WarningIcon({ size = 18, color = '#fb7185' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}

const PRIORITY_ORDER = { immediate: 0, high: 1, medium: 2, low: 3 };

const PRIORITY_CONFIG = {
  immediate: {
    label: 'Immediate',
    pillBg: 'bg-red-500/20',
    pillText: 'text-red-400',
  },
  high: {
    label: 'High',
    pillBg: 'bg-orange-500/20',
    pillText: 'text-orange-400',
  },
  medium: {
    label: 'Medium',
    pillBg: 'bg-amber-500/20',
    pillText: 'text-amber-400',
  },
  low: {
    label: 'Low',
    pillBg: 'bg-green-500/20',
    pillText: 'text-green-400',
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: (i) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.07, duration: 0.35, ease: 'easeOut' },
  }),
};

/**
 * RecommendationCard - Displays prioritised action recommendations from the
 * threat analysis, with a warning banner for critical/high severity results.
 *
 * @param {object} props
 * @param {Array}  props.recommendations - recommendations array from AnalysisResponse
 * @param {'critical'|'high'|'medium'|'low'|'safe'} [props.severity='safe']
 */
function RecommendationCard({ recommendations, severity = 'safe' }) {
  const sorted = useMemo(() => {
    if (!recommendations || recommendations.length === 0) return [];
    return [...recommendations].sort(
      (a, b) =>
        (PRIORITY_ORDER[a.priority] ?? 99) - (PRIORITY_ORDER[b.priority] ?? 99),
    );
  }, [recommendations]);

  if (sorted.length === 0) return null;

  const showWarningBanner = severity === 'critical' || severity === 'high';

  return (
    <div className="space-y-4">
      {/* Section title with shield icon */}
      <div className="flex items-center gap-2.5">
        <ShieldIcon size={18} color="#a882ff" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-[var(--text-primary)]">
          Recommended Actions
        </h3>
      </div>

      <GlassCard hover={false} padding="p-5">
        <div className="space-y-4">
          {/* Warning banner for critical / high severity */}
          {showWarningBanner && (
            <motion.div
              className="flex items-center gap-3 rounded-xl border border-red-500/20 bg-red-500/[0.08] px-4 py-3"
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <div className="flex-shrink-0">
                <WarningIcon size={18} color="#fb7185" />
              </div>
              <p className="text-xs font-medium leading-relaxed text-red-400">
                {severity === 'critical'
                  ? 'Immediate action required -- critical threat detected.'
                  : 'Immediate action required -- high-severity threat identified.'}
              </p>
            </motion.div>
          )}

          {/* Recommendation list */}
          <div className="space-y-3">
            {sorted.map((rec, idx) => {
              const config =
                PRIORITY_CONFIG[rec.priority] ?? PRIORITY_CONFIG.medium;

              return (
                <motion.div
                  key={idx}
                  className="glass-card-soft flex items-start gap-3 rounded-lg p-4"
                  custom={idx}
                  initial="hidden"
                  animate="visible"
                  variants={itemVariants}
                >
                  {/* Priority pill */}
                  <span
                    className={[
                      'mt-0.5 flex-shrink-0 rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider select-none',
                      config.pillBg,
                      config.pillText,
                    ].join(' ')}
                  >
                    {config.label}
                  </span>

                  {/* Action text + description */}
                  <div className="min-w-0 flex-1 space-y-1">
                    <p className="text-sm font-bold text-white">
                      {rec.action}
                    </p>
                    {rec.description && (
                      <p className="text-sm leading-relaxed text-[var(--text-secondary)]">
                        {rec.description}
                      </p>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </GlassCard>
    </div>
  );
}

export default RecommendationCard;
