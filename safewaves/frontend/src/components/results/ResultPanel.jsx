import { motion } from 'framer-motion';
import RiskGauge from '../shared/RiskGauge';
import SeverityBadge from '../shared/SeverityBadge';
import ConfidenceMeter from '../shared/ConfidenceMeter';
import GlassCard from '../shared/GlassCard';
import ExplanationCard from './ExplanationCard';
import ShapVisualization from './ShapVisualization';
import RecommendationCard from './RecommendationCard';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.05,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] },
  },
};

/**
 * ResultPanel - Main container for displaying threat analysis results.
 *
 * Renders RiskGauge, severity/confidence info, explanation, SHAP visualization,
 * and recommended actions in a staggered animated layout.
 *
 * @param {object} props
 * @param {object|null} props.result - The full AnalysisResponse object, or null
 */
function ResultPanel({ result }) {
  if (!result) return null;

  const {
    risk_score,
    severity,
    is_threat,
    confidence,
    explanation,
    recommendations,
    extra_data,
  } = result;

  const threatType =
    result.threat_type || extra_data?.threat_type || extra_data?.threatType || null;

  return (
    <motion.div
      className="w-full space-y-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Top section: RiskGauge + summary side panel */}
      <motion.div variants={itemVariants}>
        <GlassCard hover={false} padding="p-6">
          <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start">
            {/* Risk gauge */}
            <div className="flex-shrink-0">
              <RiskGauge score={risk_score} size={180} />
            </div>

            {/* Side panel: severity, confidence, threat type */}
            <div className="flex flex-1 flex-col justify-center gap-5">
              {/* Severity badge */}
              <div className="space-y-1.5">
                <span className="text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
                  Severity
                </span>
                <div>
                  <SeverityBadge severity={severity} size="lg" />
                </div>
              </div>

              {/* Confidence meter */}
              <ConfidenceMeter confidence={confidence} />

              {/* Threat type label */}
              {threatType && (
                <div className="space-y-1.5">
                  <span className="text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
                    Threat Type
                  </span>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">
                    {threatType}
                  </p>
                </div>
              )}

              {/* Threat status indicator */}
              <div className="flex items-center gap-2">
                <span
                  className={[
                    'h-2 w-2 rounded-full',
                    is_threat ? 'bg-red-500 animate-pulse' : 'bg-green-500',
                  ].join(' ')}
                />
                <span className="text-xs font-medium text-[var(--text-secondary)]">
                  {is_threat ? 'Threat Detected' : 'No Threat Detected'}
                </span>
              </div>
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* Explanation card */}
      {explanation && (
        <motion.div variants={itemVariants}>
          <ExplanationCard explanation={explanation} isThreat={is_threat} />
        </motion.div>
      )}

      {/* SHAP visualization */}
      {(explanation?.shap_data || explanation?.key_factors) && (
        <motion.div variants={itemVariants}>
          <ShapVisualization
            shapData={explanation.shap_data}
            keyFactors={explanation.key_factors}
          />
        </motion.div>
      )}

      {/* Recommendation card */}
      {recommendations && recommendations.length > 0 && (
        <motion.div variants={itemVariants}>
          <RecommendationCard
            recommendations={recommendations}
            severity={severity}
          />
        </motion.div>
      )}
    </motion.div>
  );
}

export default ResultPanel;
