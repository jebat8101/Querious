import streamlit as st
import subprocess
import sys
import os

# Project root (Querious/) — reliable even if Streamlit cwd differs
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GHUNT_PATH = os.path.join(_PROJECT_ROOT, "OSINT", "ghunt", "main.py")

# ----------------- UTILITY FUNCTIONS -----------------

def run_ghunt_command(command):
    """Run a GHunt command safely and capture the output."""
    try:
        ghunt_root = os.path.dirname(GHUNT_PATH)
        env = os.environ.copy()
        # Ensure bundled ghunt package is importable when not installed editable
        env["PYTHONPATH"] = os.pathsep.join(
            filter(None, [ghunt_root, env.get("PYTHONPATH", "")])
        )
        result = subprocess.run(
            [sys.executable, GHUNT_PATH] + command.split(),
            text=True,
            capture_output=True,
            cwd=ghunt_root,
            env=env,
        )
        parts = []
        if result.stdout.strip():
            parts.append(result.stdout.rstrip())
        if result.stderr.strip():
            parts.append("--- stderr ---\n" + result.stderr.rstrip())
        if not parts:
            return f"(no output, exit code {result.returncode})"
        body = "\n\n".join(parts)
        if result.returncode != 0:
            body += f"\n\n(exit code {result.returncode})"
        return body
    except Exception as e:
        return str(e)

# ----------------- GHUNT STREAMLIT APP -----------------

def ghunt_app():
    """Streamlit interface for GHunt tool."""
    st.title("GHunt OSINT")

    st.write(
        "This application provides a web interface for GHunt, allowing users to analyze "
        "Google account information based on an email address. Enter an email below to begin."
    )

    # Sidebar Options
    st.sidebar.header("GHunt Options")
    task = st.sidebar.selectbox(
        "Select Task",
        ("Email Information", "Gaia ID Information", "Drive Information", "Geolocate BSSID")
    )

    if task == "Email Information":
        st.header("Email Information")
        email = st.text_input("Enter the email address to investigate:")
        if st.button("Run GHunt on Email"):
            if email:
                st.info(f"Running GHunt on: {email}")
                output = run_ghunt_command(f"email {email}")
                st.text_area("Output:", output, height=520)
            else:
                st.warning("Please provide a valid email address.")

    elif task == "Gaia ID Information":
        st.header("Gaia ID Information")
        gaia_id = st.text_input("Enter the Gaia ID to investigate:")
        if st.button("Run GHunt on Gaia ID"):
            if gaia_id:
                st.info("Running GHunt on the provided Gaia ID...")
                output = run_ghunt_command(f"gaia {gaia_id}")
                st.text_area("Output:", output, height=520)
            else:
                st.warning("Please provide a valid Gaia ID.")

    elif task == "Drive Information":
        st.header("Drive Information")
        drive_url = st.text_input("Enter the Drive file or folder URL:")
        if st.button("Run GHunt on Drive URL"):
            if drive_url:
                st.info("Running GHunt on the provided Drive URL...")
                output = run_ghunt_command(f"drive {drive_url}")
                st.text_area("Output:", output, height=520)
            else:
                st.warning("Please provide a valid Drive URL.")

    elif task == "Geolocate BSSID":
        st.header("Geolocate BSSID")
        bssid = st.text_input("Enter the BSSID to geolocate:")
        if st.button("Run GHunt on BSSID"):
            if bssid:
                st.info("Geolocating the provided BSSID...")
                output = run_ghunt_command(f"geolocate {bssid}")
                st.text_area("Output:", output, height=520)
            else:
                st.warning("Please provide a valid BSSID.")

# Footer with Copyright
    st.markdown("""
    ---
    © 2025, All rights reserved. Developed by 051N773@M.
    """)

# ----------------- MAIN -----------------

if __name__ == "__main__":
    ghunt_app()
