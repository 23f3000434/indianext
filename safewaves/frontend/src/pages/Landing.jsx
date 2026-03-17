import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const sectionVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.08, delayChildren: 0.05 },
  },
};

const fadeUp = {
  hidden: { opacity: 0, y: 22 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] },
  },
};

const navLinks = [
  { label: 'Threats', href: '#modules' },
  { label: 'Flow', href: '#workflow' },
  { label: 'Evidence', href: '#explainability' },
  { label: 'Launch', href: '#launch' },
];

const heroPills = [
  '6 threat detection modules',
  'Severity and confidence scoring',
  'SHAP-backed explanations',
];

const threatSurfaces = [
  {
    title: 'Phishing Email',
    description: 'Detects spoofing, urgency language, suspicious links, and social engineering patterns in inbound messages.',
    accent: 'var(--purple-primary)',
    icon: MailIcon,
  },
  {
    title: 'Malicious URL',
    description: 'Flags risky domains, phishing destinations, redirect abuse, and suspicious URL structures before a click turns costly.',
    accent: 'var(--cyan-primary)',
    icon: LinkIcon,
  },
  {
    title: 'Deepfake Detection',
    description: 'Surfaces manipulated media indicators so impersonation attempts can be reviewed with visible evidence.',
    accent: 'var(--red-primary)',
    icon: CameraIcon,
  },
  {
    title: 'Prompt Injection',
    description: 'Identifies jailbreaks, instruction overrides, and other attempts to manipulate AI system behavior.',
    accent: 'var(--yellow-primary)',
    icon: TerminalIcon,
  },
  {
    title: 'Behavior Anomaly',
    description: 'Highlights unusual login history, device shifts, and suspicious access sequences that break normal patterns.',
    accent: 'var(--green-primary)',
    icon: ActivityIcon,
  },
  {
    title: 'AI Content Detection',
    description: 'Scores text for synthetic generation signals to support trust, verification, and safer human review.',
    accent: 'var(--cyan-light)',
    icon: SparkIcon,
  },
];

const workflowCards = [
  {
    step: '01',
    title: 'Accept real-world threat inputs',
    description: 'Submit message text, URLs, media, prompts, login activity, or suspicious AI-written content into the same platform.',
  },
  {
    step: '02',
    title: 'Analyze with module-specific logic',
    description: 'Each detector focuses on its own threat signals instead of forcing every problem through one generic classifier.',
  },
  {
    step: '03',
    title: 'Score the result clearly',
    description: 'Outputs include risk score, severity, and confidence so the system communicates more than a simple yes-or-no verdict.',
  },
  {
    step: '04',
    title: 'Explain why it was flagged',
    description: 'The result panel translates the model decision into readable evidence, key factors, and feature contribution signals.',
  },
  {
    step: '05',
    title: 'Recommend the safest next step',
    description: 'Users get mitigation guidance such as block, verify, escalate, or quarantine based on the threat type and severity.',
  },
];

const evidencePoints = [
  {
    title: 'Why it was flagged',
    description: 'Narrative explanations turn model output into a human cybersecurity story.',
  },
  {
    title: 'What influenced the score',
    description: 'Key factors and SHAP-style contributions show which signals increased or reduced risk.',
  },
  {
    title: 'How sure the system is',
    description: 'Confidence and severity reveal whether the alert is borderline, elevated, or urgent.',
  },
  {
    title: 'What should happen next',
    description: 'Recommendations convert the alert into practical action instead of leaving the user guessing.',
  },
];

const platformStrengths = [
  {
    title: 'Multi-threat coverage',
    description: 'Email, URL, prompt, deepfake, behavior, and AI-content detection live together in one workflow.',
  },
  {
    title: 'Explainable output',
    description: 'Every result is paired with evidence, score context, and readable reasoning.',
  },
  {
    title: 'Action guidance',
    description: 'Recommendations prioritize what to do next based on the risk that was found.',
  },
  {
    title: 'Robustness testing',
    description: 'Adversarial evaluation helps validate how consistently the system behaves under evasion-style inputs.',
  },
];

const launchRoutes = [
  {
    label: 'Overview',
    title: 'Dashboard',
    to: '/dashboard',
  },
  {
    label: 'Scan live',
    title: 'Analyzer',
    to: '/analyze',
  },
  {
    label: 'Watchlist',
    title: 'Threat Feed',
    to: '/threat-feed',
  },
  {
    label: 'Stress test',
    title: 'Adversarial Lab',
    to: '/adversarial',
  },
];

function Landing() {
  const [videoError, setVideoError] = useState(false);

  return (
    <div id="top" className="w-full bg-[var(--bg)] text-[var(--text-primary)]">
      <section className="relative isolate overflow-hidden bg-black">
        <div className="absolute inset-0 z-0 overflow-hidden">
          {!videoError && (
            <video
              autoPlay
              loop
              muted
              playsInline
              onError={() => setVideoError(true)}
              className="absolute bottom-0 left-1/2 h-[98%] w-[98%] -translate-x-1/2 object-cover opacity-72 md:h-[102%] md:w-[102%]"
              style={{ objectPosition: 'center bottom' }}
            >
              <source src="/landing-video.mp4" type="video/mp4" />
            </video>
          )}

          <div
            className="absolute inset-0"
            style={{
              background: videoError
                ? 'radial-gradient(circle at 50% 0%, rgba(168, 130, 255, 0.14), transparent 40%), #08060f'
                : 'linear-gradient(180deg, rgba(8, 6, 15, 0.32) 0%, rgba(8, 6, 15, 0.54) 42%, rgba(8, 6, 15, 0.86) 100%)',
            }}
          />
          <div
            className="absolute inset-0 opacity-80"
            style={{
              background:
                'radial-gradient(circle at 50% 22%, rgba(168, 130, 255, 0.18), transparent 28%), radial-gradient(circle at 82% 12%, rgba(0, 212, 255, 0.10), transparent 24%)',
            }}
          />
        </div>

        <div className="absolute left-1/2 top-[215px] z-10 hidden h-[384px] w-[801px] -translate-x-1/2 rounded-full bg-[rgba(8,6,15,0.94)] blur-[77.5px] lg:block" />

        <div className="relative z-20 mx-auto max-w-[1440px] px-6 md:px-10 xl:px-[120px]">
          <header className="flex min-h-[102px] flex-col justify-center gap-6 py-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center gap-6 lg:gap-16">
              <Link to="/" className="flex items-center gap-3 text-white">
                <img src="/logo.svg" alt="SafeWaves" className="h-10 w-10" />
                <div className="leading-none">
                  <div
                    className="text-[13px] uppercase tracking-[0.34em] text-white/56"
                    style={{ fontFamily: 'var(--font-mono)' }}
                  >
                    safewaves
                  </div>
                  <div className="mt-1 text-[16px] font-semibold text-white">
                    AI-powered cyber defense
                  </div>
                </div>
              </Link>

              <nav className="hidden items-center gap-2 lg:flex">
                {navLinks.map((item) => (
                  <a
                    key={item.href}
                    href={item.href}
                    className="glass-chip rounded-full px-4 py-2 text-[13px] font-medium text-[var(--text-secondary)] transition-colors duration-200 hover:text-[var(--text-primary)]"
                  >
                    {item.label}
                  </a>
                ))}
              </nav>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Link
                to="/threat-feed"
                className="glass-chip inline-flex items-center justify-center rounded-xl px-4 py-2 text-[14px] font-semibold text-[var(--text-secondary)] transition-all duration-200 hover:text-[var(--text-primary)]"
              >
                Threat Feed
              </Link>
              <Link
                to="/dashboard"
                className="inline-flex items-center justify-center rounded-xl px-4 py-2 text-[14px] font-semibold text-white transition-all duration-300 hover:-translate-y-0.5"
                style={{
                  background: 'linear-gradient(135deg, var(--purple-primary) 0%, var(--purple-dark) 100%)',
                  boxShadow: '0 16px 42px rgba(124, 92, 191, 0.28)',
                }}
              >
                Open Dashboard
              </Link>
            </div>
          </header>

          <motion.div
            className="mx-auto flex max-w-[920px] flex-col items-center pb-10 pt-20 text-center sm:pt-24 lg:pt-[158px]"
            variants={sectionVariants}
            initial="hidden"
            animate="visible"
          >
            <motion.div variants={fadeUp} className="mb-6">
              <span
                className="glass-chip inline-flex items-center gap-2 rounded-full px-4 py-2 text-[11px] uppercase tracking-[0.28em] text-white/74"
                style={{ fontFamily: 'var(--font-mono)' }}
              >
                <span className="h-2 w-2 rounded-full bg-[var(--purple-primary)] shadow-[0_0_18px_rgba(168,130,255,0.9)]" />
                Explainable multi-threat defense platform
              </span>
            </motion.div>

            <motion.div variants={fadeUp} className="space-y-3">
              <h1 className="text-[clamp(3.2rem,8vw,5rem)] font-extrabold leading-[1.02] tracking-[-0.05em] text-white">
                Detect the threat.
              </h1>
              <h2
                className="text-[clamp(3.1rem,8vw,4.9rem)] italic leading-[1.02] tracking-[-0.045em] text-white"
                style={{ fontFamily: 'var(--font-display)' }}
              >
                Explain the risk.
              </h2>
              <p className="mx-auto max-w-[670px] text-[17px] leading-7 text-[var(--text-secondary)] sm:text-[18px]">
                SafeWaves brings phishing, malicious URL, deepfake, prompt injection, anomaly,
                and AI-content analysis into one interface, then shows the score, evidence,
                confidence, and recommended next action for every alert.
              </p>
            </motion.div>

            <motion.div variants={fadeUp} className="mt-8 flex flex-wrap items-center justify-center gap-[18px]">
              <Link
                to="/dashboard"
                className="inline-flex items-center justify-center rounded-xl px-7 py-[14px] text-[16px] font-semibold text-white transition-all duration-300 hover:-translate-y-0.5"
                style={{
                  background: 'linear-gradient(135deg, var(--purple-primary) 0%, var(--purple-dark) 100%)',
                  boxShadow: '0 18px 48px rgba(124, 92, 191, 0.32)',
                }}
              >
                Explore Dashboard
              </Link>
              <Link
                to="/analyze"
                className="glass-chip inline-flex items-center justify-center rounded-xl px-7 py-[14px] text-[16px] font-semibold text-[var(--text-primary)] transition-all duration-300 hover:-translate-y-0.5"
              >
                Start Analysis
              </Link>
            </motion.div>

            <motion.div variants={fadeUp} className="mt-8 flex flex-wrap items-center justify-center gap-3">
              {heroPills.map((pill) => (
                <span
                  key={pill}
                  className="glass-chip rounded-full px-4 py-2 text-[12px] text-[var(--text-secondary)]"
                >
                  {pill}
                </span>
              ))}
            </motion.div>
          </motion.div>

          <motion.div
            variants={fadeUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            className="mx-auto w-full max-w-[1163px] pb-10 pt-6"
          >
            <div
              className="glass-card-strong rounded-[24px] border p-[22.5px]"
              style={{
                borderColor: 'rgba(255, 255, 255, 0.10)',
                background: 'rgba(255, 255, 255, 0.05)',
                boxShadow: '0 35px 120px rgba(0, 0, 0, 0.45)',
              }}
            >
              <div className="rounded-[18px] border border-white/[0.08] bg-[#09070f]/88 p-5 sm:p-6">
                <div className="flex flex-col gap-3 border-b border-white/[0.06] pb-4 md:flex-row md:items-center md:justify-between">
                  <div>
                    <div
                      className="text-[11px] uppercase tracking-[0.28em] text-[var(--purple-light)]"
                      style={{ fontFamily: 'var(--font-mono)' }}
                    >
                      Platform snapshot
                    </div>
                    <div className="mt-2 text-[24px] font-semibold tracking-[-0.03em] text-white">
                      One workflow for score, evidence, and response
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <StatusChip label="Threat feed live" accent="var(--cyan-primary)" />
                    <StatusChip label="6 modules active" accent="var(--purple-primary)" />
                    <StatusChip label="Adversarial lab" accent="var(--yellow-primary)" />
                  </div>
                </div>

                <div className="mt-5 grid gap-4 xl:grid-cols-[0.92fr_1.2fr_0.92fr]">
                  <PreviewCard
                    title="Risk snapshot"
                    eyebrow="Severity + confidence"
                    accent="var(--red-primary)"
                  >
                    <div className="flex items-center gap-5">
                      <div
                        className="grid h-28 w-28 place-items-center rounded-full border"
                        style={{
                          borderColor: 'rgba(239, 68, 68, 0.32)',
                          background:
                            'radial-gradient(circle at 30% 20%, rgba(239, 68, 68, 0.35), rgba(8, 6, 15, 0.96) 65%)',
                          boxShadow: '0 0 45px rgba(239, 68, 68, 0.22)',
                        }}
                      >
                        <div className="text-center">
                          <div className="text-[34px] font-bold text-white">92</div>
                          <div
                            className="text-[10px] uppercase tracking-[0.25em] text-white/65"
                            style={{ fontFamily: 'var(--font-mono)' }}
                          >
                            Risk
                          </div>
                        </div>
                      </div>

                      <div className="space-y-3 text-sm text-white/78">
                        <div className="flex items-center gap-2">
                          <span className="rounded-full border border-red-400/22 bg-red-400/12 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-red-200">
                            Critical
                          </span>
                          <span className="text-white/58">Confidence 0.91</span>
                        </div>
                        <p>The output is designed to make urgency obvious without losing clarity.</p>
                      </div>
                    </div>

                    <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
                      <MiniMetric label="Threat type" value="Prompt injection" />
                      <MiniMetric label="Suggested action" value="Escalate now" />
                    </div>
                  </PreviewCard>

                  <PreviewCard
                    title="Evidence trail"
                    eyebrow="Key factors + SHAP signal"
                    accent="var(--purple-primary)"
                  >
                    <div className="space-y-3">
                      {[
                        'Instruction override language sharply increases risk.',
                        'Sensitive prompt disclosure request is clearly present.',
                        'Authority spoofing and urgency cues push the score higher.',
                        'Response guidance is prioritized by severity level.',
                      ].map((item, index) => (
                        <div
                          key={item}
                          className="flex items-start gap-3 rounded-2xl border border-white/[0.06] bg-white/[0.03] px-4 py-3"
                        >
                          <div
                            className="mt-0.5 grid h-6 w-6 place-items-center rounded-full text-[11px] font-semibold text-black"
                            style={{
                              background: index < 2 ? 'var(--purple-primary)' : 'var(--cyan-primary)',
                            }}
                          >
                            {index + 1}
                          </div>
                          <p className="text-sm leading-6 text-white/82">{item}</p>
                        </div>
                      ))}
                    </div>
                  </PreviewCard>

                  <PreviewCard
                    title="Next actions"
                    eyebrow="Response guidance"
                    accent="var(--green-primary)"
                  >
                    <div className="space-y-3">
                      {[
                        'Block or quarantine the input before it spreads.',
                        'Verify sender identity or source through a trusted channel.',
                        'Escalate severe incidents into the response workflow.',
                      ].map((item) => (
                        <div
                          key={item}
                          className="rounded-2xl border border-white/[0.06] bg-white/[0.03] px-4 py-3 text-sm leading-6 text-white/80"
                        >
                          {item}
                        </div>
                      ))}
                    </div>
                  </PreviewCard>
                </div>

                <div className="mt-4 grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
                  <PreviewCard
                    title="Threat coverage"
                    eyebrow="Active modules"
                    accent="var(--cyan-primary)"
                  >
                    <div className="flex flex-wrap gap-2">
                      {[
                        'Phishing email',
                        'Malicious URL',
                        'Deepfake checks',
                        'Prompt injection',
                        'Behavior anomaly',
                        'AI content',
                      ].map((item) => (
                        <span
                          key={item}
                          className="rounded-full border border-white/[0.08] bg-white/[0.03] px-3 py-2 text-[12px] text-white/75"
                        >
                          {item}
                        </span>
                      ))}
                    </div>
                  </PreviewCard>

                  <PreviewCard
                    title="Navigation"
                    eyebrow="Working routes"
                    accent="var(--yellow-primary)"
                  >
                    <div className="grid gap-2 sm:grid-cols-2">
                      {['Dashboard', 'Analyzer', 'Threat Feed', 'Adversarial Lab'].map((item) => (
                        <div
                          key={item}
                          className="rounded-2xl border border-white/[0.06] bg-white/[0.03] px-4 py-3 text-sm text-white/78"
                        >
                          {item}
                        </div>
                      ))}
                    </div>
                  </PreviewCard>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <div
        className="relative overflow-hidden bg-[var(--bg)]"
        style={{
          backgroundImage:
            'radial-gradient(circle at 18% 0%, rgba(168, 130, 255, 0.12), transparent 28%), radial-gradient(circle at 82% 8%, rgba(0, 212, 255, 0.08), transparent 26%)',
        }}
      >
        <div className="mx-auto max-w-[1440px] px-6 py-20 md:px-10 xl:px-[120px] xl:py-24">
          <motion.section
            id="modules"
            className="scroll-mt-16"
            variants={sectionVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.18 }}
          >
            <motion.div variants={fadeUp}>
              <SectionHeading
                eyebrow="What It Detects"
                title="What can SafeWaves detect?"
                subtitle="The platform focuses on high-impact modern cyber risks by combining phishing, malicious URL, deepfake, prompt injection, behavior, and AI-content analysis in one place."
              />
            </motion.div>

            <div className="mt-10 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {threatSurfaces.map((surface) => (
                <motion.div key={surface.title} variants={fadeUp}>
                  <SurfaceCard {...surface} />
                </motion.div>
              ))}
            </div>
          </motion.section>

          <motion.section
            id="workflow"
            className="mt-24 scroll-mt-16"
            variants={sectionVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.16 }}
          >
            <motion.div variants={fadeUp}>
              <SectionHeading
                eyebrow="How It Works"
                title="How does a suspicious input move through the platform?"
                subtitle="A single submission flows from intake to analysis, explainability, and recommended action so the full security story stays visible end to end."
              />
            </motion.div>

            <div className="mt-10 grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
              {workflowCards.map((card) => (
                <motion.div key={card.step} variants={fadeUp}>
                  <WorkflowCard {...card} />
                </motion.div>
              ))}
            </div>
          </motion.section>

          <motion.section
            id="explainability"
            className="mt-24 scroll-mt-16"
            variants={sectionVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.16 }}
          >
            <motion.div variants={fadeUp}>
              <SectionHeading
                eyebrow="Why It Was Flagged"
                title="Why was this marked risky?"
                subtitle="SafeWaves does not stop at classification. Every alert includes the score, confidence, evidence, and the clearest next step so the decision can be understood and acted on."
              />
            </motion.div>

            <motion.div
              variants={fadeUp}
              className="mt-10 grid gap-4 lg:grid-cols-[1.05fr_0.95fr]"
            >
              <div className="glass-card rounded-[28px] p-7">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <div
                      className="text-[11px] uppercase tracking-[0.28em] text-[var(--purple-light)]"
                      style={{ fontFamily: 'var(--font-mono)' }}
                    >
                      Explanation layer
                    </div>
                    <h3
                      className="mt-3 text-[28px] font-semibold tracking-[-0.03em] text-white"
                    >
                      The result panel is built to answer the alert, not hide it
                    </h3>
                  </div>
                  <div
                    className="hidden h-14 w-14 shrink-0 items-center justify-center rounded-2xl sm:flex"
                    style={{
                      background: 'rgba(168, 130, 255, 0.12)',
                      border: '1px solid rgba(168, 130, 255, 0.18)',
                    }}
                  >
                    <GraphIcon className="h-6 w-6 text-[var(--purple-primary)]" />
                  </div>
                </div>

                <div className="mt-8 grid gap-4 sm:grid-cols-2">
                  {evidencePoints.map((point) => (
                    <ExplainabilityPoint
                      key={point.title}
                      title={point.title}
                      description={point.description}
                    />
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <div className="glass-card rounded-[28px] p-6">
                  <div
                    className="text-[11px] uppercase tracking-[0.28em] text-[var(--cyan-light)]"
                    style={{ fontFamily: 'var(--font-mono)' }}
                  >
                    Evidence snapshot
                  </div>
                  <div className="mt-5 space-y-3">
                    {[
                      { label: 'Risk score', value: '0 to 100 severity ladder' },
                      { label: 'Confidence', value: 'Clearer certainty signal' },
                      { label: 'Key factors', value: 'Most influential traits' },
                      { label: 'SHAP view', value: 'Visual contribution panel' },
                    ].map((item) => (
                      <div
                        key={item.label}
                        className="flex items-center justify-between rounded-2xl border border-white/[0.06] bg-white/[0.03] px-4 py-3 text-sm text-white/78"
                      >
                        <span>{item.label}</span>
                        <span className="text-white">{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  {platformStrengths.map((item) => (
                    <StrengthCard
                      key={item.title}
                      title={item.title}
                      description={item.description}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          </motion.section>

          <motion.section
            id="launch"
            className="relative mt-24 overflow-hidden rounded-[36px] border border-white/[0.08] scroll-mt-16"
            variants={sectionVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.16 }}
            style={{
              background:
                'linear-gradient(135deg, rgba(79, 33, 125, 0.98) 0%, rgba(116, 74, 186, 0.94) 38%, rgba(34, 15, 58, 0.98) 100%)',
              boxShadow: '0 34px 120px rgba(12, 6, 24, 0.42)',
            }}
          >
            <div
              className="absolute inset-0"
              style={{
                background:
                  'repeating-linear-gradient(90deg, rgba(255, 255, 255, 0.05) 0px, rgba(255, 255, 255, 0.05) 1px, transparent 1px, transparent 58px)',
              }}
            />
            <div
              className="absolute inset-0"
              style={{
                background:
                  'radial-gradient(circle at 50% 18%, rgba(234, 213, 255, 0.18), transparent 24%), radial-gradient(circle at 82% 82%, rgba(56, 189, 248, 0.12), transparent 28%), linear-gradient(180deg, rgba(255,255,255,0.04), rgba(14,8,28,0.18))',
              }}
            />

            <div className="relative px-6 py-14 md:px-10 md:py-16 xl:px-16 xl:py-20">
              <motion.div variants={fadeUp} className="text-center">
                <div
                  className="text-[11px] uppercase tracking-[0.32em] text-white/68"
                  style={{ fontFamily: 'var(--font-mono)' }}
                >
                  Open The Product
                </div>

                <div
                  className="mx-auto mt-8 max-w-[980px] text-[clamp(2.85rem,8vw,7rem)] uppercase leading-[0.88] tracking-[-0.08em] text-white"
                  style={{ fontFamily: 'var(--font-mono)' }}
                >
                  <div>Open the</div>
                  <div className="flex items-center justify-center gap-3 md:gap-5">
                    <span>Next</span>
                    <LaunchOrbIcon className="h-[0.8em] w-[0.8em] shrink-0 text-white/72" />
                    <span>Wave</span>
                  </div>
                  <div>Then trace</div>
                  <div className="text-[#efe3ff]">The signal</div>
                </div>

                <p className="mx-auto mt-6 max-w-[360px] text-[15px] leading-6 text-white/74">
                  Less talk. Pick a route and move.
                </p>

                <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
                  <Link
                    to="/dashboard"
                    className="inline-flex items-center justify-center rounded-full border border-white/15 bg-white/10 px-6 py-3 text-[13px] font-semibold uppercase tracking-[0.24em] text-white transition-all duration-300 hover:-translate-y-0.5 hover:bg-white/14"
                    style={{ fontFamily: 'var(--font-mono)' }}
                  >
                    Open Dashboard
                  </Link>
                  <a
                    href="#top"
                    className="inline-flex items-center justify-center rounded-full border border-white/14 bg-transparent px-5 py-3 text-[13px] font-semibold uppercase tracking-[0.24em] text-white/78 transition-colors duration-300 hover:text-white"
                    style={{ fontFamily: 'var(--font-mono)' }}
                  >
                    Back to top
                  </a>
                </div>
              </motion.div>

              <motion.div
                variants={fadeUp}
                className="mt-14 grid gap-6 border-t border-white/14 pt-6 lg:grid-cols-[0.78fr_1.22fr] lg:items-end"
              >
                <div className="max-w-[300px]">
                  <div
                    className="text-[11px] uppercase tracking-[0.28em] text-white/58"
                    style={{ fontFamily: 'var(--font-mono)' }}
                  >
                    Live routes
                  </div>
                  <p className="mt-3 text-sm leading-6 text-white/72">
                    Open any live screen.
                  </p>
                </div>

                <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                  {launchRoutes.map((route) => (
                    <motion.div key={route.title} variants={fadeUp}>
                      <LaunchRouteTile {...route} />
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </div>
          </motion.section>
        </div>
      </div>
    </div>
  );
}

function SectionHeading({ eyebrow, title, subtitle }) {
  return (
    <div className="max-w-[860px]">
      <div
        className="text-[11px] uppercase tracking-[0.28em] text-[var(--purple-light)]"
        style={{ fontFamily: 'var(--font-mono)' }}
      >
        {eyebrow}
      </div>
      <h2
        className="mt-4 text-[clamp(2rem,5vw,3.3rem)] font-semibold leading-[1.05] tracking-[-0.04em] text-white"
      >
        {title}
      </h2>
      <p className="mt-4 max-w-[760px] text-[16px] leading-7 text-[var(--text-secondary)] sm:text-[17px]">
        {subtitle}
      </p>
    </div>
  );
}

function SurfaceCard({ title, description, accent, icon: Icon }) {
  return (
    <motion.div whileHover={{ y: -6 }} className="glass-card h-full rounded-[28px] p-6">
      <div
        className="flex h-14 w-14 items-center justify-center rounded-2xl"
        style={{
          background: `${accent}16`,
          border: `1px solid ${accent}2b`,
          color: accent,
        }}
      >
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="mt-5 text-[22px] font-semibold tracking-[-0.03em] text-white">
        {title}
      </h3>
      <p className="mt-3 text-[15px] leading-7 text-[var(--text-secondary)]">
        {description}
      </p>
    </motion.div>
  );
}

function WorkflowCard({ step, title, description }) {
  return (
    <motion.div whileHover={{ y: -6 }} className="glass-card h-full rounded-[28px] p-6">
      <div className="flex items-center justify-between gap-4">
        <span
          className="text-[11px] uppercase tracking-[0.26em] text-[var(--text-muted)]"
          style={{ fontFamily: 'var(--font-mono)' }}
        >
          System step
        </span>
        <span className="text-[18px] font-semibold text-[var(--purple-primary)]">
          {step}
        </span>
      </div>
      <h3 className="mt-5 text-[24px] font-semibold leading-[1.15] tracking-[-0.03em] text-white">
        {title}
      </h3>
      <p className="mt-4 text-[15px] leading-7 text-[var(--text-secondary)]">
        {description}
      </p>
    </motion.div>
  );
}

function ExplainabilityPoint({ title, description }) {
  return (
    <div className="rounded-[24px] border border-white/[0.08] bg-white/[0.03] p-5">
      <div className="text-[13px] font-semibold text-white">
        {title}
      </div>
      <p className="mt-2 text-[14px] leading-6 text-[var(--text-secondary)]">
        {description}
      </p>
    </div>
  );
}

function StrengthCard({ title, description }) {
  return (
    <div className="glass-card-soft rounded-[24px] p-5">
      <div
        className="text-[11px] uppercase tracking-[0.24em] text-[var(--purple-light)]"
        style={{ fontFamily: 'var(--font-mono)' }}
      >
        Platform strength
      </div>
      <div className="mt-3 text-[18px] font-semibold tracking-[-0.03em] text-white">
        {title}
      </div>
      <p className="mt-2 text-[14px] leading-6 text-[var(--text-secondary)]">
        {description}
      </p>
    </div>
  );
}

function LaunchRouteTile({ label, title, to }) {
  return (
    <motion.div whileHover={{ y: -6 }} className="h-full">
      <Link
        to={to}
        className="group flex h-full min-h-[132px] flex-col justify-between rounded-[24px] border border-white/[0.11] bg-[rgba(27,12,43,0.28)] p-5 backdrop-blur-[18px] transition-all duration-300 hover:border-white/[0.18] hover:bg-[rgba(34,16,56,0.34)]"
      >
        <div className="flex items-center justify-between gap-3">
          <span
            className="text-[10px] uppercase tracking-[0.28em] text-white/56"
            style={{ fontFamily: 'var(--font-mono)' }}
          >
            {label}
          </span>
          <ArrowUpRightIcon className="h-4 w-4 text-[var(--purple-light)] transition-transform duration-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
        </div>

        <div>
          <div className="text-[22px] font-semibold tracking-[-0.04em] text-white">
            {title}
          </div>
          <div
            className="mt-4 h-px w-16"
            style={{
              background: 'linear-gradient(90deg, rgba(239, 227, 255, 0.95) 0%, rgba(239, 227, 255, 0) 100%)',
            }}
          />
        </div>
      </Link>
    </motion.div>
  );
}

function PreviewCard({ title, eyebrow, accent, children }) {
  return (
    <div className="rounded-[24px] border border-white/[0.08] bg-white/[0.025] p-5">
      <div
        className="text-[10px] uppercase tracking-[0.28em]"
        style={{ fontFamily: 'var(--font-mono)', color: accent }}
      >
        {eyebrow}
      </div>
      <div className="mt-2 text-[18px] font-semibold tracking-[-0.03em] text-white">
        {title}
      </div>
      <div className="mt-5">{children}</div>
    </div>
  );
}

function MiniMetric({ label, value }) {
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-white/[0.03] px-4 py-3">
      <div
        className="text-[11px] uppercase tracking-[0.2em] text-white/46"
        style={{ fontFamily: 'var(--font-mono)' }}
      >
        {label}
      </div>
      <div className="mt-2 text-white/84">
        {value}
      </div>
    </div>
  );
}

function StatusChip({ label, accent }) {
  return (
    <span
      className="inline-flex items-center gap-2 rounded-full border px-3 py-2 text-[11px] uppercase tracking-[0.22em] text-white/76"
      style={{
        fontFamily: 'var(--font-mono)',
        borderColor: `${accent}33`,
        background: `${accent}14`,
      }}
    >
      <span
        className="h-2 w-2 rounded-full"
        style={{ background: accent, boxShadow: `0 0 16px ${accent}` }}
      />
      {label}
    </span>
  );
}

function ArrowUpRightIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M7 17L17 7" />
      <path d="M8 7h9v9" />
    </svg>
  );
}

function LaunchOrbIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 120 120" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="60" cy="60" r="46" strokeWidth="2.6" />
      <ellipse cx="60" cy="60" rx="18" ry="46" strokeWidth="1.8" opacity="0.82" />
      <ellipse cx="60" cy="60" rx="33" ry="46" strokeWidth="1.6" opacity="0.58" />
      <path d="M14 60h92" strokeWidth="1.9" opacity="0.82" />
      <path d="M20 40c10 6.67 23.33 10 40 10s30-3.33 40-10" strokeWidth="1.7" opacity="0.6" />
      <path d="M20 80c10-6.67 23.33-10 40-10s30 3.33 40 10" strokeWidth="1.7" opacity="0.6" />
      <path d="M29 26c7.33 13.33 18 20 31 20s23.67-6.67 31-20" strokeWidth="1.4" opacity="0.42" />
      <path d="M29 94c7.33-13.33 18-20 31-20s23.67 6.67 31 20" strokeWidth="1.4" opacity="0.42" />
    </svg>
  );
}

function MailIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
    </svg>
  );
}

function LinkIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
    </svg>
  );
}

function CameraIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
      <circle cx="12" cy="13" r="4" />
    </svg>
  );
}

function TerminalIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="4 17 10 11 4 5" />
      <line x1="12" y1="19" x2="20" y2="19" />
    </svg>
  );
}

function ActivityIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </svg>
  );
}

function SparkIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2a4 4 0 0 1 4 4c0 1.95-1.4 3.57-3.25 3.92a1 1 0 0 0-.75.97V13" />
      <circle cx="12" cy="17" r="1.25" />
      <path d="M4.2 4.2C2.8 5.6 2 7.7 2 10c0 5.52 4.48 10 10 10s10-4.48 10-10c0-2.3-.8-4.4-2.2-5.8" />
    </svg>
  );
}

function GraphIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 3v18h18" />
      <path d="M7 15l4-4 3 3 5-7" />
    </svg>
  );
}

export default Landing;
