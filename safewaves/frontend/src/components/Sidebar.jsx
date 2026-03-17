import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: DashboardIcon },
  { to: '/analyze', label: 'Analyze', icon: AnalyzeIcon },
  { to: '/threat-feed', label: 'Threat Feed', icon: ThreatFeedIcon },
  { to: '/adversarial', label: 'Adversarial', icon: AdversarialIcon },
];

function Sidebar() {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.aside
      initial={false}
      animate={{ width: expanded ? 220 : 68 }}
      transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
      className="fixed left-4 top-4 bottom-4 z-50 flex flex-col rounded-2xl overflow-hidden"
      style={{
        background: 'rgba(14, 11, 24, 0.55)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 24px rgba(168, 130, 255, 0.06)',
      }}
    >
      {/* Logo / Brand */}
      <Link to="/" className="flex items-center px-4 py-5 border-b border-white/[0.06] gap-3 min-h-[68px]">
        <img
          src="/logo.svg"
          alt="SafeWaves"
          className="w-8 h-8 shrink-0"
        />
        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: 'auto' }}
              exit={{ opacity: 0, width: 0 }}
              transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
              className="overflow-hidden whitespace-nowrap"
            >
              <span className="gradient-text text-lg font-bold tracking-tight">
                safewaves
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </Link>

      {/* Navigation */}
      <nav className="flex-1 flex flex-col gap-1 px-2 py-3">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/dashboard'}
            title={label}
            className={({ isActive }) =>
              `group relative flex items-center gap-3 rounded-xl text-sm font-medium transition-all duration-200 ${expanded ? 'px-3 py-2.5' : 'px-0 py-2.5 justify-center'
              } ${isActive
                ? 'bg-[rgba(168,130,255,0.15)] text-[var(--purple-light)] border border-[rgba(168,130,255,0.15)]'
                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/[0.06] border border-transparent'
              }`
            }
          >
            <Icon className="w-[20px] h-[20px] shrink-0" />
            <AnimatePresence>
              {expanded && (
                <motion.span
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: 'auto' }}
                  exit={{ opacity: 0, width: 0 }}
                  transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
                  className="overflow-hidden whitespace-nowrap"
                >
                  {label}
                </motion.span>
              )}
            </AnimatePresence>

            {/* Tooltip on hover when collapsed */}
            {!expanded && (
              <div className="pointer-events-none absolute left-full ml-3 px-2.5 py-1 rounded-lg text-xs font-medium text-[var(--text-primary)] opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap"
                style={{
                  background: 'rgba(14, 11, 24, 0.85)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  backdropFilter: 'blur(12px)',
                }}
              >
                {label}
              </div>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Expand / Collapse Toggle */}
      <div className="px-2 py-3 border-t border-white/[0.06]">
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-center gap-2 py-2 rounded-xl text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/[0.06] transition-all duration-200"
        >
          <motion.svg
            animate={{ rotate: expanded ? 180 : 0 }}
            transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
            className="w-4 h-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="9 18 15 12 9 6" />
          </motion.svg>
          <AnimatePresence>
            {expanded && (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
                className="overflow-hidden whitespace-nowrap text-xs font-medium"
              >
                Collapse
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>
    </motion.aside>
  );
}

// ── Inline SVG Icons ───────────────────────────────

function DashboardIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="9" rx="1.5" />
      <rect x="14" y="3" width="7" height="5" rx="1.5" />
      <rect x="3" y="16" width="7" height="5" rx="1.5" />
      <rect x="14" y="12" width="7" height="9" rx="1.5" />
    </svg>
  );
}

function AnalyzeIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="7" />
      <path d="M21 21l-4.35-4.35" />
      <path d="M11 8v6M8 11h6" />
    </svg>
  );
}

function ThreatFeedIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
    </svg>
  );
}

function AdversarialIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      <path d="M9 12l2 2 4-4" />
    </svg>
  );
}

export default Sidebar;
