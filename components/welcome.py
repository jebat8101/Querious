"""Cosmos Studio–style preloader welcome (Awwwards-inspired)."""

import streamlit as st


def welcome_screen() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

#MainMenu, header[data-testid="stHeader"], footer { visibility: hidden !important; height: 0 !important; }
section[data-testid="stSidebar"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }

.block-container {
  padding: 0.5rem 0.35rem 1rem !important;
  max-width: 100% !important;
  min-height: 100vh !important;
  position: relative;
  z-index: 1;
}

.stApp {
  background: #030306 !important;
}

/* —— Backdrop: deep space + nebula glows —— */
.cs-backdrop {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
  background: #030306;
}

.cs-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.45;
  animation: cs-drift 18s ease-in-out infinite;
}
.cs-glow-1 {
  width: min(90vw, 720px);
  height: min(90vw, 720px);
  left: -15%;
  top: -20%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.5) 0%, transparent 70%);
}
.cs-glow-2 {
  width: min(70vw, 560px);
  height: min(70vw, 560px);
  right: -10%;
  bottom: -15%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.35) 0%, transparent 68%);
  animation-delay: -9s;
}

@keyframes cs-drift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(4%, 3%) scale(1.06); }
}

.cs-stars {
  position: absolute;
  inset: 0;
  opacity: 0.4;
  animation: cs-twinkle 5s ease-in-out infinite;
  background-image:
    radial-gradient(1px 1px at 8% 12%, rgba(255,255,255,0.9), transparent),
    radial-gradient(1px 1px at 22% 44%, rgba(255,255,255,0.5), transparent),
    radial-gradient(1px 1px at 38% 8%, rgba(255,255,255,0.7), transparent),
    radial-gradient(1px 1px at 55% 28%, rgba(255,255,255,0.45), transparent),
    radial-gradient(1px 1px at 72% 18%, rgba(255,255,255,0.85), transparent),
    radial-gradient(1px 1px at 88% 42%, rgba(255,255,255,0.5), transparent),
    radial-gradient(1px 1px at 15% 72%, rgba(255,255,255,0.55), transparent),
    radial-gradient(1px 1px at 42% 88%, rgba(255,255,255,0.75), transparent),
    radial-gradient(1px 1px at 68% 76%, rgba(255,255,255,0.4), transparent),
    radial-gradient(1px 1px at 92% 82%, rgba(255,255,255,0.65), transparent),
    radial-gradient(1px 1px at 30% 58%, rgba(255,255,255,0.35), transparent),
    radial-gradient(1px 1px at 58% 52%, rgba(255,255,255,0.6), transparent),
    radial-gradient(1.5px 1.5px at 48% 38%, rgba(196, 181, 253, 0.8), transparent),
    radial-gradient(1px 1px at 78% 58%, rgba(255,255,255,0.5), transparent),
    radial-gradient(1px 1px at 5% 88%, rgba(255,255,255,0.45), transparent),
    radial-gradient(1px 1px at 95% 12%, rgba(255,255,255,0.55), transparent);
  background-size: 100% 100%;
}

@keyframes cs-twinkle {
  0%, 100% { opacity: 0.28; }
  50% { opacity: 0.48; }
}

.cs-grain {
  position: absolute;
  inset: 0;
  opacity: 0.055;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)'/%3E%3C/svg%3E");
}

.cs-vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 75% 65% at 50% 50%, transparent 0%, rgba(0,0,0,0.55) 100%);
}

/* —— Orbital ring loader (studio preloader) —— */
.cs-orbit-wrap {
  width: min(120px, 22vw);
  height: min(120px, 22vw);
  margin: 0 auto 1.75rem;
  position: relative;
  animation: cs-fade-in 1s ease 0.05s both;
}

.cs-orbit-wrap svg {
  width: 100%;
  height: 100%;
  display: block;
  filter: drop-shadow(0 0 12px rgba(129, 140, 248, 0.35));
}

.cs-orbit-spin {
  transform-origin: 50px 50px;
  animation: cs-orbit-rotate 1.35s linear infinite;
}

@keyframes cs-orbit-rotate {
  to { transform: rotate(360deg); }
}

@keyframes cs-fade-in {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

/* —— Hero type —— */
.cs-hero {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: min(8vh, 3rem) 0.75rem 0;
}

.cs-kicker {
  font-family: "DM Sans", system-ui, sans-serif;
  font-size: clamp(20px, 1.5vw, 11px);
  font-weight: 500;
  letter-spacing: 0.48em;
  text-transform: uppercase;
  color: rgba(226, 232, 240, 0.45);
  margin: 0 0 1.25rem;
  animation: cs-fade-in 0.9s ease 0.12s both;
}

.cs-title {
  font-family: "DM Sans", system-ui, sans-serif;
  font-size: clamp(5.5rem, 16vw, 20.5rem);
  font-weight: 700;
  letter-spacing: -0.04em;
  line-height: 0.95;
  margin: 0 0 1.5rem;
  color: #f8fafc;
  text-shadow:
    0 0 40px rgba(129, 140, 248, 0.25),
    0 0 80px rgba(56, 189, 248, 0.12),
    0 2px 0 rgba(255,255,255,0.06);
  animation: cs-fade-in 1s ease 0.08s both, cs-title-glow 5s ease-in-out infinite 1s;
}

@keyframes cs-title-glow {
  0%, 100% { text-shadow: 0 0 40px rgba(129, 140, 248, 0.22), 0 0 80px rgba(56, 189, 248, 0.1), 0 2px 0 rgba(255,255,255,0.06); }
  50% { text-shadow: 0 0 56px rgba(129, 140, 248, 0.35), 0 0 100px rgba(56, 189, 248, 0.18), 0 2px 0 rgba(255,255,255,0.08); }
}

.cs-line {
  width: min(180px, 38vw);
  height: 1px;
  margin: 0 auto;
  background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.35), transparent);
  position: relative;
  overflow: hidden;
  animation: cs-fade-in 1s ease 0.28s both;
}

.cs-line::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(196, 181, 253, 0.7), transparent);
  animation: cs-line-sweep 2.4s ease-in-out infinite;
}

@keyframes cs-line-sweep {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* Bottom edge shimmer (preloader bar) */
.cs-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 2px;
  z-index: 2;
  pointer-events: none;
  background: rgba(15, 23, 42, 0.9);
  overflow: hidden;
}
.cs-bar::after {
  content: "";
  position: absolute;
  top: 0;
  left: -40%;
  width: 40%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(129, 140, 248, 0.9), rgba(56, 189, 248, 0.6), transparent);
  animation: cs-bar-slide 2.8s ease-in-out infinite;
}
@keyframes cs-bar-slide {
  0% { left: -40%; }
  100% { left: 100%; }
}
</style>

<div class="cs-backdrop" aria-hidden="true">
  <div class="cs-glow cs-glow-1"></div>
  <div class="cs-glow cs-glow-2"></div>
  <div class="cs-stars"></div>
  <div class="cs-grain"></div>
  <div class="cs-vignette"></div>
</div>

<div class="cs-bar" aria-hidden="true"></div>

<div class="cs-hero">
  <div class="cs-orbit-wrap">
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <defs>
        <linearGradient id="csStroke" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#818cf8"/>
          <stop offset="50%" stop-color="#38bdf8"/>
          <stop offset="100%" stop-color="#c4b5fd"/>
        </linearGradient>
      </defs>
      <circle cx="50" cy="50" r="44" fill="none" stroke="rgba(148,163,184,0.12)" stroke-width="1"/>
      <g class="cs-orbit-spin">
        <circle cx="50" cy="50" r="44" fill="none" stroke="url(#csStroke)" stroke-width="2"
          stroke-linecap="round" stroke-dasharray="70 206" transform="rotate(-90 50 50)"/>
      </g>
    </svg>
  </div>
  <p class="cs-kicker">Loading</p>
  <h1 class="cs-title">QUERIOUS</h1>
  <p class="cs-kicker">Multi-App Osint Toolkit</p>
  <div class="cs-line"></div>
</div>
""",
        unsafe_allow_html=True,
    )

    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("Enter", type="primary", use_container_width=True, key="welcome_enter"):
            st.session_state.welcome_acknowledged = True
            st.rerun()
