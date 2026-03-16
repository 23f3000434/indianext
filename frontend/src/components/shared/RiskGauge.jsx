import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { useEffect } from 'react';

/**
 * Returns the colour associated with a given risk score.
 */
function getScoreColor(score) {
  if (score <= 20) return '#22c55e'; // green
  if (score <= 40) return '#eab308'; // yellow
  if (score <= 60) return '#f59e0b'; // amber
  if (score <= 80) return '#f97316'; // orange
  return '#ef4444'; // red
}

/**
 * Returns a human-readable severity label for a risk score.
 */
function getSeverityLabel(score) {
  if (score <= 20) return 'Safe';
  if (score <= 40) return 'Low';
  if (score <= 60) return 'Medium';
  if (score <= 80) return 'High';
  return 'Critical';
}

/**
 * RiskGauge - Animated circular SVG gauge that visualises a 0-100 risk score.
 *
 * @param {object} props
 * @param {number} props.score       - Value between 0 and 100
 * @param {number} [props.size=200]  - Diameter in px
 * @param {string} [props.label='Risk Score'] - Label shown beneath the number
 */
function RiskGauge({ score = 0, size = 200, label = 'Risk Score' }) {
  const clampedScore = Math.max(0, Math.min(100, score));
  const color = getScoreColor(clampedScore);
  const severityLabel = getSeverityLabel(clampedScore);

  // SVG geometry
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const center = size / 2;

  // Animated motion value: drives both the arc and the displayed number.
  const motionScore = useMotionValue(0);
  const dashOffset = useTransform(
    motionScore,
    (v) => circumference - (v / 100) * circumference,
  );
  const displayScore = useTransform(motionScore, (v) => Math.round(v));

  useEffect(() => {
    const controls = animate(motionScore, clampedScore, {
      duration: 1.4,
      ease: [0.25, 0.46, 0.45, 0.94],
    });
    return controls.stop;
  }, [clampedScore, motionScore]);

  return (
    <motion.div
      className="flex flex-col items-center gap-2"
      initial={{ opacity: 0, scale: 0.85 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          className="rotate-[-90deg]"
        >
          {/* Glow filter */}
          <defs>
            <filter id="riskGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Background track */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={strokeWidth}
          />

          {/* Animated progress arc */}
          <motion.circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            style={{ strokeDashoffset: dashOffset }}
            filter="url(#riskGlow)"
          />
        </svg>

        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="font-bold tracking-tight"
            style={{
              fontSize: size * 0.22,
              color,
              textShadow: `0 0 20px ${color}44`,
            }}
          >
            {displayScore}
          </motion.span>

          <span
            className="font-semibold uppercase tracking-widest"
            style={{
              fontSize: size * 0.065,
              color,
              opacity: 0.9,
            }}
          >
            {severityLabel}
          </span>
        </div>
      </div>

      {/* Label */}
      <span className="text-xs font-medium uppercase tracking-widest text-[var(--text-muted)]">
        {label}
      </span>
    </motion.div>
  );
}

export default RiskGauge;
