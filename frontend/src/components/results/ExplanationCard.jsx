import { motion } from 'framer-motion';
import GlassCard from '../shared/GlassCard';

/** Inline SVG lightbulb icon. */
function LightbulbIcon({ size = 18, color = '#a882ff' }) {
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
      <path d="M9 18h6" />
      <path d="M10 22h4" />
      <path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z" />
    </svg>
  );
}

/** Inline SVG up-arrow icon for negative impact (increases risk). */
function ArrowUpIcon({ size = 14, color = '#fb7185' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 19V5" />
      <path d="m5 12 7-7 7 7" />
    </svg>
  );
}

/** Inline SVG down-arrow icon for positive impact (decreases risk). */
function ArrowDownIcon({ size = 14, color = '#22c55e' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 5v14" />
      <path d="m19 12-7 7-7-7" />
    </svg>
  );
}

/** Inline SVG minus icon for neutral impact. */
function MinusIcon({ size = 14, color = '#5c5672' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M5 12h14" />
    </svg>
  );
}

const IMPACT_CONFIG = {
  negative: {
    borderColor: 'border-l-red-500',
    bg: 'bg-red-500/[0.04]',
    icon: ArrowUpIcon,
    iconColor: '#fb7185',
    label: 'Increases risk',
  },
  positive: {
    borderColor: 'border-l-green-500',
    bg: 'bg-green-500/[0.04]',
    icon: ArrowDownIcon,
    iconColor: '#22c55e',
    label: 'Decreases risk',
  },
  neutral: {
    borderColor: 'border-l-gray-500',
    bg: 'bg-[rgba(18,14,30,0.42)]',
    icon: MinusIcon,
    iconColor: '#5c5672',
    label: 'Neutral',
  },
};

const factorVariants = {
  hidden: { opacity: 0, x: -12 },
  visible: (i) => ({
    opacity: 1,
    x: 0,
    transition: { delay: i * 0.08, duration: 0.35, ease: 'easeOut' },
  }),
};

/**
 * ExplanationCard - Displays the natural-language explanation and key factors
 * from the threat analysis result.
 *
 * @param {object} props
 * @param {object} props.explanation - The explanation object from AnalysisResponse
 * @param {boolean} [props.isThreat=false] - Whether the result was flagged as a threat
 */
function ExplanationCard({ explanation, isThreat = false }) {
  if (!explanation) return null;

  const { summary, key_factors } = explanation;
  const title = isThreat ? 'Why This Was Flagged' : 'Analysis Summary';

  return (
    <div className="space-y-4">
      {/* Section title with lightbulb icon */}
      <div className="flex items-center gap-2.5">
        <LightbulbIcon size={18} color="#a882ff" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-[var(--text-primary)]">
          {title}
        </h3>
      </div>

      {/* Summary highlighted box */}
      {summary && (
        <GlassCard hover={false} padding="p-5">
          <div className="rounded-lg border border-purple-500/20 bg-purple-500/[0.06] px-4 py-3">
            <p className="text-sm leading-relaxed text-[var(--text-secondary)]">
              {summary}
            </p>
          </div>
        </GlassCard>
      )}

      {/* Key factors list */}
      {key_factors && key_factors.length > 0 && (
        <div className="space-y-2">
          <span className="text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
            Key Factors
          </span>
          <div className="space-y-2">
            {key_factors.map((factor, index) => {
              const config =
                IMPACT_CONFIG[factor.impact] ?? IMPACT_CONFIG.neutral;
              const ImpactIcon = config.icon;

              return (
                <motion.div
                  key={`${factor.feature}-${index}`}
                  className={[
                    'flex items-start gap-3 rounded-xl border border-white/[0.06] border-l-[3px] p-4',
                    config.borderColor,
                    config.bg,
                  ].join(' ')}
                  custom={index}
                  initial="hidden"
                  animate="visible"
                  variants={factorVariants}
                >
                  {/* Impact direction icon */}
                  <div className="mt-0.5 flex-shrink-0">
                    <ImpactIcon size={14} color={config.iconColor} />
                  </div>

                  {/* Content */}
                  <div className="min-w-0 flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-[var(--text-primary)]">
                        {factor.feature}
                      </span>
                      {factor.value != null && (
                        <span className="rounded-md bg-white/[0.06] px-2 py-0.5 font-mono text-xs text-[var(--text-muted)]">
                          {String(factor.value)}
                        </span>
                      )}
                    </div>
                    {factor.description && (
                      <p className="text-xs leading-relaxed text-[var(--text-secondary)]">
                        {factor.description}
                      </p>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default ExplanationCard;
