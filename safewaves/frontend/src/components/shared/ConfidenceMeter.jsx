import { motion } from 'framer-motion';

/**
 * Returns the bar colour based on confidence value.
 */
function getConfidenceColor(confidence) {
  if (confidence >= 0.8) return { bar: '#22c55e', glow: 'rgba(34,197,94,0.25)' };
  if (confidence >= 0.5) return { bar: '#f59e0b', glow: 'rgba(245,158,11,0.25)' };
  return { bar: '#ef4444', glow: 'rgba(239,68,68,0.25)' };
}

/**
 * ConfidenceMeter - Horizontal bar that fills to represent a confidence value.
 *
 * @param {object} props
 * @param {number} props.confidence  - Value between 0 and 1
 * @param {string} [props.label='Confidence'] - Label text
 */
function ConfidenceMeter({ confidence = 0, label = 'Confidence' }) {
  const clamped = Math.max(0, Math.min(1, confidence));
  const pct = Math.round(clamped * 100);
  const { bar, glow } = getConfidenceColor(clamped);

  return (
    <div className="w-full space-y-2">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
          {label}
        </span>
        <span
          className="text-sm font-bold tabular-nums"
          style={{ color: bar }}
        >
          {pct}%
        </span>
      </div>

      {/* Track */}
      <div className="relative h-2 w-full rounded-full bg-white/[0.06] overflow-hidden">
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{
            backgroundColor: bar,
            boxShadow: `0 0 12px ${glow}`,
          }}
          initial={{ width: '0%' }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 1, ease: [0.25, 0.46, 0.45, 0.94] }}
        />
      </div>
    </div>
  );
}

export default ConfidenceMeter;
