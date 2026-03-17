import { motion } from 'framer-motion';

/**
 * GradientButton - Themed action button with gradient fills, loading state,
 * and hover scale / glow effects.
 *
 * @param {object}  props
 * @param {React.ReactNode} props.children
 * @param {Function} [props.onClick]
 * @param {'primary'|'secondary'|'danger'} [props.variant='primary']
 * @param {boolean} [props.disabled=false]
 * @param {boolean} [props.loading=false]
 * @param {string}  [props.className]
 * @param {string}  [props.type='button']
 */

const VARIANT_CLASSES = {
  primary: [
    'bg-gradient-to-r from-purple-600 to-indigo-600',
    'text-white',
    'shadow-lg shadow-purple-500/20',
    'hover:shadow-purple-500/40',
    'hover:from-purple-500 hover:to-indigo-500',
  ].join(' '),
  secondary: [
    'bg-transparent',
    'border border-purple-500/40',
    'text-purple-300',
    'hover:bg-purple-500/10',
    'hover:border-purple-400/60',
  ].join(' '),
  danger: [
    'bg-gradient-to-r from-red-600 to-rose-600',
    'text-white',
    'shadow-lg shadow-red-500/20',
    'hover:shadow-red-500/40',
    'hover:from-red-500 hover:to-rose-500',
  ].join(' '),
};

function GradientButton({
  children,
  onClick,
  variant = 'primary',
  disabled = false,
  loading = false,
  className = '',
  type = 'button',
}) {
  const variantClasses = VARIANT_CLASSES[variant] ?? VARIANT_CLASSES.primary;
  const isDisabled = disabled || loading;

  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={isDisabled}
      whileHover={isDisabled ? {} : { scale: 1.03 }}
      whileTap={isDisabled ? {} : { scale: 0.97 }}
      className={[
        'relative inline-flex items-center justify-center gap-2',
        'px-5 py-2.5 rounded-xl',
        'text-sm font-semibold tracking-wide',
        'transition-all duration-300 cursor-pointer',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#08060f]',
        variantClasses,
        isDisabled ? 'opacity-50 cursor-not-allowed saturate-50' : '',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      {/* Loading spinner */}
      {loading && (
        <svg
          className="animate-spin h-4 w-4 shrink-0"
          viewBox="0 0 24 24"
          fill="none"
        >
          <circle
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray="50 14"
            opacity="0.8"
          />
        </svg>
      )}

      {children}
    </motion.button>
  );
}

export default GradientButton;
