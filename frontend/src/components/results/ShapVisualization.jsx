import { useMemo } from 'react';
import { motion } from 'framer-motion';
import GlassCard from '../shared/GlassCard';

const POSITIVE_COLOR = '#a882ff'; // purple -- increases risk
const NEGATIVE_COLOR = '#22d3ee'; // cyan   -- decreases risk
const MAX_FEATURES = 8;

const barVariants = {
  hidden: { width: 0 },
  visible: (i) => ({
    width: '100%',
    transition: {
      delay: i * 0.07,
      duration: 0.5,
      ease: [0.25, 0.46, 0.45, 0.94],
    },
  }),
};

/**
 * ShapVisualization - Renders a SHAP-style feature importance chart using
 * plain Tailwind-styled divs (no Recharts dependency).
 *
 * Features are sorted by absolute SHAP value (descending) and limited to the
 * top 8. Positive values extend right from center (purple), negative values
 * extend left from center (cyan).
 *
 * @param {object} props
 * @param {object} [props.shapData]   - { features: string[], values: number[], base_value: number }
 * @param {Array}  [props.keyFactors] - key_factors array (fallback when no shap_data)
 */
function ShapVisualization({ shapData, keyFactors }) {
  const hasShapData =
    shapData &&
    Array.isArray(shapData.features) &&
    Array.isArray(shapData.values) &&
    shapData.features.length > 0;

  // Build chart data: pair features with values, sort by |value| desc, cap at MAX_FEATURES
  const chartData = useMemo(() => {
    if (!hasShapData) return [];

    return shapData.features
      .map((feature, i) => ({
        feature,
        value: shapData.values[i] ?? 0,
      }))
      .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
      .slice(0, MAX_FEATURES);
  }, [shapData, hasShapData]);

  const maxAbsValue = useMemo(
    () =>
      chartData.length > 0
        ? Math.max(...chartData.map((d) => Math.abs(d.value)))
        : 0,
    [chartData],
  );

  // Fall back to key_factors if no SHAP data and key_factors exist
  const fallbackData = useMemo(() => {
    if (hasShapData || !keyFactors || keyFactors.length === 0) return [];

    return keyFactors
      .map((factor) => {
        const syntheticValue =
          factor.impact === 'negative'
            ? 0.5
            : factor.impact === 'positive'
              ? -0.5
              : 0;
        return { feature: factor.feature, value: syntheticValue };
      })
      .slice(0, MAX_FEATURES);
  }, [hasShapData, keyFactors]);

  const displayData = chartData.length > 0 ? chartData : fallbackData;
  const effectiveMax =
    chartData.length > 0
      ? maxAbsValue
      : displayData.length > 0
        ? Math.max(...displayData.map((d) => Math.abs(d.value)))
        : 0;

  if (displayData.length === 0) return null;

  return (
    <div className="space-y-4">
      {/* Section title */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-[var(--text-primary)]">
          Feature Importance Analysis
        </h3>
        {hasShapData && shapData.base_value != null && (
          <span className="font-mono text-xs text-[var(--text-muted)]">
            base: {Number(shapData.base_value).toFixed(3)}
          </span>
        )}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-5">
        <div className="flex items-center gap-1.5">
          <span
            className="h-2.5 w-2.5 rounded-sm"
            style={{ backgroundColor: POSITIVE_COLOR }}
          />
          <span className="text-[11px] text-[var(--text-muted)]">
            Increases risk
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <span
            className="h-2.5 w-2.5 rounded-sm"
            style={{ backgroundColor: NEGATIVE_COLOR }}
          />
          <span className="text-[11px] text-[var(--text-muted)]">
            Decreases risk
          </span>
        </div>
      </div>

      {/* Chart */}
      <GlassCard hover={false} padding="p-5">
        <div className="space-y-3">
          {displayData.map((entry, idx) => {
            const pct =
              effectiveMax > 0
                ? (Math.abs(entry.value) / effectiveMax) * 100
                : 0;
            const isPositive = entry.value >= 0;
            const color = isPositive ? POSITIVE_COLOR : NEGATIVE_COLOR;

            return (
              <div key={`${entry.feature}-${idx}`} className="flex items-center gap-3">
                {/* Feature name */}
                <span className="w-32 flex-shrink-0 truncate text-right text-xs text-[var(--text-secondary)]">
                  {entry.feature}
                </span>

                {/* Bar track */}
                <div className="relative flex h-6 flex-1 items-center">
                  {/* Center line */}
                  <div className="absolute left-1/2 top-0 h-full w-px bg-white/[0.1]" />

                  {/* Animated bar */}
                  <div
                    className="absolute top-1 h-4"
                    style={{
                      width: `${pct / 2}%`,
                      ...(isPositive
                        ? { left: '50%' }
                        : { right: '50%' }),
                    }}
                  >
                    <motion.div
                      className="h-full rounded"
                      style={{
                        backgroundColor: color,
                        boxShadow: `0 0 10px ${color}44`,
                        originX: isPositive ? 0 : 1,
                      }}
                      custom={idx}
                      initial="hidden"
                      animate="visible"
                      variants={barVariants}
                    />
                  </div>
                </div>

                {/* Value text */}
                <span
                  className="w-16 flex-shrink-0 text-right font-mono text-xs font-medium"
                  style={{ color }}
                >
                  {entry.value >= 0 ? '+' : ''}
                  {entry.value.toFixed(3)}
                </span>
              </div>
            );
          })}
        </div>
      </GlassCard>
    </div>
  );
}

export default ShapVisualization;
