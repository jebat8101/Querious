# Querious

**Multi-App OSINT Toolkit** — a Streamlit web dashboard that unifies multiple open-source intelligence tools in one interface.

<img width="1408" height="768" alt="Querious OSINT Toolkit" src="https://github.com/user-attachments/assets/d11f4074-4271-4598-b5c5-302a75a70852" />

Repository: [https://github.com/jebat8101/Querious](https://github.com/jebat8101/Querious.git)

---

## Overview

| Aspect | Description |
|--------|-------------|
| **Type** | Multi-app OSINT toolkit (web UI) |
| **Stack** | Python + Streamlit |
| **Usage** | Pick a category → pick a tool → enter your target (email, username, phone, image, etc.) |
| **Entry point** | `main.py` → `components/` (UI) → `OSINT/` (tool modules) |

After launch, a welcome screen is shown. Click **Enter** to open the OSINT dashboard.

---

## Project structure

```
Querious/
├── main.py                    # Streamlit entry point
├── setup.sh                   # Automated install script
├── requirements.txt           # Core dependencies
├── requirements-optional.txt  # Heavy ML deps (torch, etc.) — optional
├── components/
│   ├── welcome.py             # Welcome / splash screen
│   └── homepage.py            # Sidebar navigation + tool routing
└── OSINT/
    ├── ghunt/                 # Google account OSINT
    ├── sherlock/              # Username search across sites
    ├── holeheweb/             # Email account verification
    ├── socialpulse/           # Phone number validation
    ├── kizunafinder/          # Social media search
    ├── gvision/               # Reverse image search (Google Vision)
    ├── waybackWeb/            # Wayback / archived tweets
    ├── Hawkerweb/              # Multi-source email lookup
    ├── tele/                  # Telegram checker / scraper
    └── usernametoolweb/       # Additional username OSINT
```

---

## Tools in the dashboard

| Category | Tool | Description |
|----------|------|-------------|
| **Phone** | SocialPulse | Phone validation and related info |
| **Phone** | Telegram Phone Checker | Check if a number is on Telegram |
| **Social Media** | Kizuna Finder | Social profile search |
| **Social Media** | Wayback Tweets | Archived tweets via Wayback |
| **Email** | Holehe (Email Verification) | Find registered accounts for an email |
| **Email** | GHunt | Google account OSINT (profile, Maps, public calendar, etc.) |
| **Username** | Sherlock | Username search across hundreds of sites |
| **Username** | Username Search App | Additional username OSINT |
| **Lookup** | Hawker OSINT | Email checks on multiple services (GitHub, etc.) |
| **Geolocation** | GVision | Reverse image search (landmarks, web entities) |

---

## Requirements

- **OS:** Linux (recommended), macOS, or Windows with WSL
- **Python:** 3.10+ (3.11 recommended)
- **Git**
- **Disk/RAM:** ~2–4 GB for a standard install; **+2 GB+** if you install `requirements-optional.txt` (PyTorch)
- **Network:** Internet access for `pip install` and external APIs

---

## Installation (step by step)

### Step 1 — Clone the repository

```bash
git clone https://github.com/jebat8101/Querious.git
cd Querious
```

### Step 2 — Ensure Python and venv are available

```bash
python3 --version   # should be 3.10 or newer
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git   # Debian / Kali
```

### Step 3 — Run the setup script (recommended)

This creates `.venv`, installs dependencies, and installs **GHunt** and **Sherlock** in editable mode:

```bash
chmod +x setup.sh
./setup.sh
```

What `setup.sh` does:

1. Creates a virtualenv at `.venv` (if missing)
2. Runs `pip install -r requirements.txt`
3. Runs `pip install -e OSINT/ghunt`
4. Runs `pip install -e OSINT/sherlock`

### Step 4 — Activate the virtualenv

```bash
source .venv/bin/activate
```

### Step 5 — (Optional) Install heavy ML dependencies

Only if you need torch/transformers for specific ML features:

```bash
pip install -r requirements-optional.txt
```

> The default install **excludes** PyTorch/CUDA to save disk space.

### Step 6 — Run the application

```bash
streamlit run main.py
```

Open in your browser: **http://localhost:8501**

To allow access from other machines:

```bash
streamlit run main.py --server.address 0.0.0.0 --server.port 8501
```

---

## Manual installation (without `setup.sh`)

```bash
cd Querious
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
pip install -e OSINT/ghunt
pip install -e OSINT/sherlock
streamlit run main.py
```

---

## Post-install configuration

### GHunt (Google OSINT)

For fuller Maps and calendar results, log in once via the CLI:

```bash
source .venv/bin/activate
python OSINT/ghunt/main.py login
```

Then use **GHunt OSINT Tool** in the dashboard (tasks: Email, Gaia ID, Drive, Geolocate BSSID).

> Messages such as `[-] No review` or `[-] No public Google Calendar` usually mean no public data exists for the target — not an install error.

### GVision (reverse image search)

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **Cloud Vision API**
3. Upload your service account JSON key via the **GVision** app sidebar

### Telegram tools

Get an **API ID** and **API Hash** from [my.telegram.org](https://my.telegram.org), then enter them in the UI or set environment variables:

```bash
export APP_API_ID="your_id"
export APP_API_HASH="your_hash"
```

---

## GitHub Codespaces / Dev Container

The repo includes `.devcontainer/` — port **8501** is forwarded automatically. After the container is ready:

```bash
streamlit run main.py
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Disk full during `pip install` | Run `pip cache purge`, free space, then re-run `./setup.sh` |
| Import errors for `ghunt` / `sherlock` | Run `pip install -e OSINT/ghunt` and `pip install -e OSINT/sherlock` |
| Streamlit not reloading files | Config uses `fileWatcherType = "poll"` in `.streamlit/config.toml` |
| GHunt returns no Maps data | Run `python OSINT/ghunt/main.py login` first |
| Tool needs an API key | Check each tool’s sidebar (e.g. GVision, Kizuna Finder) |

---

## Quick start flow

```
Clone repo → ./setup.sh → source .venv/bin/activate → streamlit run main.py
→ Enter welcome screen → Select category & tool → Run OSINT
```

---

## License & upstream tools

Bundled tools retain their own licenses. Notable upstream projects:

- [GHunt](https://github.com/mxrch/GHunt) — Google account OSINT
- [Sherlock](https://github.com/sherlock-project/sherlock) — Username search

Use responsibly and only on targets you are authorized to investigate.
