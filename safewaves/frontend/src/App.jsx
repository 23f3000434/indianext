import { lazy, Suspense } from 'react';
import { BrowserRouter, Navigate, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import Sidebar from './components/Sidebar';
import VideoBackground from './components/VideoBackground';

// ── Lazy-loaded Pages ──────────────────────────────
const Landing = lazy(() => import('./pages/Landing'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Analyze = lazy(() => import('./pages/Analyze'));
const ThreatFeed = lazy(() => import('./pages/ThreatFeed'));
const AdversarialTest = lazy(() => import('./pages/AdversarialTest'));

// ── Page Transition Wrapper ────────────────────────
const pageVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.2, ease: 'easeIn' } },
};

function PageWrapper({ children }) {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="w-full"
    >
      {children}
    </motion.div>
  );
}

// ── Loading Fallback ───────────────────────────────
function LoadingFallback() {
  return (
    <div className="flex-1 flex items-center justify-center min-h-screen">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-2 border-[var(--purple-primary)] border-t-transparent rounded-full animate-spin" />
        <p className="text-[var(--text-secondary)] text-sm font-medium tracking-wide">
          Loading...
        </p>
      </div>
    </div>
  );
}

// ── Animated Routes ────────────────────────────────
function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route
          path="/"
          element={
            <PageWrapper>
              <Suspense fallback={<LoadingFallback />}>
                <Landing />
              </Suspense>
            </PageWrapper>
          }
        />
        <Route
          path="/dashboard"
          element={
            <PageWrapper>
              <Suspense fallback={<LoadingFallback />}>
                <Dashboard />
              </Suspense>
            </PageWrapper>
          }
        />
        <Route
          path="/analyze"
          element={
            <PageWrapper>
              <Suspense fallback={<LoadingFallback />}>
                <Analyze />
              </Suspense>
            </PageWrapper>
          }
        />
        <Route
          path="/threat-feed"
          element={
            <PageWrapper>
              <Suspense fallback={<LoadingFallback />}>
                <ThreatFeed />
              </Suspense>
            </PageWrapper>
          }
        />
        <Route
          path="/adversarial"
          element={
            <PageWrapper>
              <Suspense fallback={<LoadingFallback />}>
                <AdversarialTest />
              </Suspense>
            </PageWrapper>
          }
        />
        <Route path="/app" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  );
}

function AppLayout() {
  const location = useLocation();
  const isLandingPage = location.pathname === '/';

  return (
    <>
      {!isLandingPage && <VideoBackground />}
      {!isLandingPage && <Sidebar />}

      <div
        className={
          isLandingPage
            ? 'relative z-10 flex-1 min-h-screen w-full'
            : 'relative z-10 flex-1 min-h-screen min-w-0 pl-[88px]'
        }
      >
        <main className={isLandingPage ? 'w-full' : 'w-full overflow-y-auto'}>
          <AnimatedRoutes />
        </main>
      </div>
    </>
  );
}

// ── App Root ───────────────────────────────────────
function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}

export default App;
