import { motion, AnimatePresence } from 'framer-motion';

/**
 * LoadingSpinner - Pulsing analysis-in-progress indicator with a shield icon.
 *
 * @param {object} props
 * @param {string} [props.message='Analyzing threat...'] - Status message
 */
function LoadingSpinner({ message = 'Analyzing threat...' }) {
  return (
    <AnimatePresence>
      <motion.div
        className="flex flex-col items-center justify-center gap-6"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
      >
        {/* Spinner ring + shield icon */}
        <div className="relative flex items-center justify-center">
          {/* Outer pulsing glow */}
          <motion.div
            className="absolute w-24 h-24 rounded-full"
            style={{
              background:
                'radial-gradient(circle, rgba(168,130,255,0.18) 0%, transparent 70%)',
            }}
            animate={{ scale: [1, 1.35, 1], opacity: [0.6, 0.25, 0.6] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          />

          {/* Spinning ring */}
          <motion.svg
            width={64}
            height={64}
            viewBox="0 0 64 64"
            className="absolute"
            animate={{ rotate: 360 }}
            transition={{ duration: 1.6, repeat: Infinity, ease: 'linear' }}
          >
            <circle
              cx="32"
              cy="32"
              r="28"
              fill="none"
              stroke="rgba(255,255,255,0.06)"
              strokeWidth="3"
            />
            <circle
              cx="32"
              cy="32"
              r="28"
              fill="none"
              stroke="url(#spinnerGradient)"
              strokeWidth="3"
              strokeLinecap="round"
              strokeDasharray="120 60"
            />
            <defs>
              <linearGradient id="spinnerGradient" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#a882ff" />
                <stop offset="100%" stopColor="#6366f1" />
              </linearGradient>
            </defs>
          </motion.svg>

          {/* Shield icon */}
          <motion.svg
            width={28}
            height={28}
            viewBox="0 0 24 24"
            fill="none"
            stroke="#a882ff"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            animate={{ opacity: [0.7, 1, 0.7] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          >
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </motion.svg>
        </div>

        {/* Message */}
        <motion.p
          className="text-sm font-medium text-[var(--text-secondary)] tracking-wide"
          animate={{ opacity: [0.6, 1, 0.6] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        >
          {message}
        </motion.p>
      </motion.div>
    </AnimatePresence>
  );
}

export default LoadingSpinner;
