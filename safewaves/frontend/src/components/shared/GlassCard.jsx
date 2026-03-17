import { motion } from 'framer-motion';

/**
 * GlassCard - Reusable glass morphism card wrapper for the safewaves dashboard.
 *
 * @param {object}  props
 * @param {React.ReactNode} props.children
 * @param {string}  [props.className]    - Additional Tailwind classes
 * @param {boolean} [props.hover=true]   - Enable hover lift / glow effect
 * @param {Function} [props.onClick]     - Click handler (also adds cursor-pointer)
 * @param {string}  [props.padding='p-6'] - Padding utility class
 */
function GlassCard({
  children,
  className = '',
  hover = true,
  onClick,
  padding = 'p-6',
}) {
  const baseClasses = [
    'glass-card',
    'rounded-2xl',
    padding,
  ];

  const hoverClasses = hover
    ? [
      'hover:border-purple-400/30',
      'hover:-translate-y-1',
      'hover:shadow-lg',
      'hover:shadow-purple-500/5',
      'transition-all',
      'duration-300',
    ]
    : [];

  const interactiveClasses = onClick ? ['cursor-pointer'] : [];

  const combinedClassName = [
    ...baseClasses,
    ...hoverClasses,
    ...interactiveClasses,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <motion.div
      className={combinedClassName}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] }}
      onClick={onClick}
    >
      {children}
    </motion.div>
  );
}

export default GlassCard;
