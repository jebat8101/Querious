"""Onto-style welcome screen shown before the login form."""

import streamlit as st


def _welcome_overlay_styles() -> None:
    """Minimal chrome for an editorial full-screen welcome (Onto-style)."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&display=swap');
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 0 !important;
                max-width: 100% !important;
            }
            section[data-testid="stSidebar"] { display: none !important; }
            div[data-testid="stToolbar"] { visibility: hidden !important; }
            header[data-testid="stHeader"] { background: transparent !important; }
            .stApp {
                background: #050505 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def welcome_screen() -> None:
    """Awwwards Onto Loading–inspired welcome: motion, staggered type, reveal line."""
    _welcome_overlay_styles()

    st.iframe(
        """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; }
    .onto-root {
      font-family: 'Syne', system-ui, sans-serif;
      background: #050505;
      color: #f4f4f4;
      min-height: 72vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 2rem 1.5rem 1rem;
      overflow: hidden;
    }
    .onto-word {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 0.02em;
      font-weight: 800;
      font-size: clamp(2.25rem, 10vw, 5.5rem);
      line-height: 0.95;
      letter-spacing: -0.04em;
    }
    .onto-char {
      display: inline-block;
      opacity: 0;
      transform: translate3d(0, 48px, 0) rotateX(-12deg);
      animation: onto-rise 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes onto-rise {
      to {
        opacity: 1;
        transform: translate3d(0, 0, 0) rotateX(0deg);
      }
    }
    .onto-sub {
      margin-top: 1.75rem;
      font-size: clamp(0.85rem, 2.2vw, 1.05rem);
      font-weight: 400;
      letter-spacing: 0.35em;
      text-transform: uppercase;
      color: #8a8a8a;
      opacity: 0;
      animation: onto-fade 1s ease 0.9s forwards;
    }
    @keyframes onto-fade {
      to { opacity: 1; }
    }
    .onto-line-wrap {
      margin-top: 2.5rem;
      width: min(420px, 88vw);
      height: 2px;
      background: rgba(255,255,255,0.08);
      position: relative;
      overflow: hidden;
      border-radius: 1px;
    }
    .onto-line-fill {
      position: absolute;
      left: 0;
      top: 0;
      height: 100%;
      width: 100%;
      transform-origin: left center;
      transform: scaleX(0);
      background: linear-gradient(90deg, #ffffff 0%, #b8b8b8 50%, #ffffff 100%);
      animation: onto-draw 1.35s cubic-bezier(0.65, 0, 0.35, 1) 0.35s forwards;
    }
    @keyframes onto-draw {
      to { transform: scaleX(1); }
    }
    .onto-foot {
      margin-top: 2rem;
      font-size: 0.75rem;
      letter-spacing: 0.12em;
      color: #5c5c5c;
      opacity: 0;
      animation: onto-fade 0.8s ease 1.4s forwards;
    }
  </style>
</head>
<body>
  <div class="onto-root">
    <div class="onto-word" aria-label="QUERIOUS">
      <span class="onto-char" style="animation-delay: 0.10s;">Q</span>
      <span class="onto-char" style="animation-delay: 0.12s;">U</span>
      <span class="onto-char" style="animation-delay: 0.19s;">E</span>
      <span class="onto-char" style="animation-delay: 0.26s;">R</span>
      <span class="onto-char" style="animation-delay: 0.33s;">I</span>
      <span class="onto-char" style="animation-delay: 0.40s;">O</span>
      <span class="onto-char" style="animation-delay: 0.47s;">U</span>
      <span class="onto-char" style="animation-delay: 0.54s;">S</span>
    </div>
    <p class="onto-sub">Tools Suite</p>
    <div class="onto-line-wrap" aria-hidden="true">
      <div class="onto-line-fill"></div>
    </div>
    <p class="onto-foot">Power By Eclogic</p>
  </div>
</body>
</html>
        """,
        height=520,
    )

    st.markdown(
        "<div style='text-align:center;color:#666;font-size:0.8rem;margin-bottom:0.75rem;'>Continue to sign in</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Enter", type="primary", use_container_width=True, key="welcome_enter"):
            st.session_state.welcome_acknowledged = True
            st.rerun()
