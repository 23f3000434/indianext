/**
 * SeverityBadge - Pill-shaped badge indicating threat severity level.
 *
 * @param {object} props
 * @param {'critical'|'high'|'medium'|'low'|'safe'} props.severity
 * @param {'sm'|'md'|'lg'} [props.size='md']
 */

const SEVERITY_CONFIG = {
  critical: {
    label: 'Critical',
    dot: 'bg-red-500',
    text: 'text-red-400',
    bg: 'bg-red-500/10',
    border: 'border-red-500/20',
    pulse: true,
  },
  high: {
    label: 'High',
    dot: 'bg-orange-500',
    text: 'text-orange-400',
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/20',
    pulse: true,
  },
  medium: {
    label: 'Medium',
    dot: 'bg-amber-500',
    text: 'text-amber-400',
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/20',
    pulse: false,
  },
  low: {
    label: 'Low',
    dot: 'bg-yellow-500',
    text: 'text-yellow-400',
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/20',
    pulse: false,
  },
  safe: {
    label: 'Safe',
    dot: 'bg-green-500',
    text: 'text-green-400',
    bg: 'bg-green-500/10',
    border: 'border-green-500/20',
    pulse: false,
  },
};

const SIZE_CLASSES = {
  sm: { wrapper: 'px-2 py-0.5 text-[10px]', dot: 'w-1.5 h-1.5' },
  md: { wrapper: 'px-3 py-1 text-xs', dot: 'w-2 h-2' },
  lg: { wrapper: 'px-4 py-1.5 text-sm', dot: 'w-2.5 h-2.5' },
};

function SeverityBadge({ severity = 'safe', size = 'md' }) {
  const config = SEVERITY_CONFIG[severity] ?? SEVERITY_CONFIG.safe;
  const sizeConfig = SIZE_CLASSES[size] ?? SIZE_CLASSES.md;

  return (
    <span
      className={[
        'inline-flex items-center gap-1.5 rounded-full border font-semibold uppercase tracking-wider select-none',
        config.bg,
        config.border,
        config.text,
        sizeConfig.wrapper,
      ].join(' ')}
    >
      {/* Dot indicator */}
      <span className="relative flex">
        {config.pulse && (
          <span
            className={[
              'absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping',
              config.dot,
            ].join(' ')}
          />
        )}
        <span
          className={['relative inline-flex rounded-full', config.dot, sizeConfig.dot].join(' ')}
        />
      </span>

      {config.label}
    </span>
  );
}

export default SeverityBadge;
