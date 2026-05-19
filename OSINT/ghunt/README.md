# GHunt (bundled in Querious)

Google account OSINT framework — embedded for the Querious Streamlit dashboard.

Upstream: https://github.com/mxrch/GHunt

## Install (Querious)

Dependencies are installed via the project root:

```bash
cd /home/kali/tools/Querious
pip install -r requirements.txt
pip install -e OSINT/ghunt
```

## CLI

```bash
python OSINT/ghunt/main.py --help
python OSINT/ghunt/main.py login    # required for Maps; helps Calendar API
python OSINT/ghunt/main.py email target@example.com
```

## Public Google Calendar

The email module checks for a **public** calendar in three ways:

1. Authenticated Calendar API (GHunt session / `login`)
2. Public Calendar API v3 (API key only — no extra cookies)
3. Public iCal feed (`/calendar/ical/{email}/public/basic.ics`)

If you see `[-] No public Google Calendar`, the target has not published their calendar under **Access permissions for event details** in [Calendar share settings](https://calendar.google.com/calendar/u/0/r/settings/share).
