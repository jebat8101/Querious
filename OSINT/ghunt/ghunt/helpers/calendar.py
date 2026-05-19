import json
from copy import deepcopy
from urllib.parse import quote

from beautifultable import BeautifulTable
from dateutil.relativedelta import relativedelta
import httpx

from datetime import datetime
from typing import *
from ghunt.parsers.calendar import Calendar, CalendarEvents, CalendarEvent
from ghunt.objects.base import GHuntCreds
from ghunt.objects.utils import TMPrinter
from ghunt.apis.calendar import CalendarHttp
from ghunt.helpers.knowledge import get_api_key
from ghunt.helpers.utils import get_datetime_utc


def _merge_events_page(events: CalendarEvents, page_data: dict) -> str:
    batch = CalendarEvents()
    batch._scrape(page_data)
    events.items.extend(batch.items)
    if not events.summary and page_data.get("summary"):
        events.summary = page_data.get("summary")
    if not events.time_zone and page_data.get("timeZone"):
        events.time_zone = page_data.get("timeZone")
    if page_data.get("accessRole"):
        events.access_role = page_data.get("accessRole")
    return page_data.get("nextPageToken") or ""


async def _fetch_public_via_api_key(
    as_client: httpx.AsyncClient, email_address: str
) -> Tuple[bool, Optional[Calendar], Optional[CalendarEvents]]:
    """Public calendars: Calendar API v3 with API key only (no session cookies)."""
    api_key = get_api_key("calendar")
    cal_url = f"https://www.googleapis.com/calendar/v3/calendars/{quote(email_address, safe='')}"
    events_url = f"https://www.googleapis.com/calendar/v3/calendars/{quote(email_address, safe='')}/events"

    try:
        cal_resp = await as_client.get(cal_url, params={"key": api_key}, timeout=30.0)
        if cal_resp.status_code != 200:
            return False, None, None
        cal_data = cal_resp.json()
        if "error" in cal_data:
            return False, None, None

        calendar = Calendar()
        calendar._scrape(cal_data)

        events = CalendarEvents()
        page_token = ""
        while True:
            params: Dict[str, Any] = {
                "key": api_key,
                "singleEvents": True,
                "maxAttendees": 1,
                "maxResults": 2500,
            }
            if page_token:
                params["pageToken"] = page_token
            ev_resp = await as_client.get(events_url, params=params, timeout=60.0)
            if ev_resp.status_code != 200:
                break
            ev_data = ev_resp.json()
            if "error" in ev_data:
                if events.items:
                    break
                return False, None, None
            page_token = _merge_events_page(events, ev_data)
            if not page_token:
                break

        return True, calendar, events
    except (httpx.HTTPError, json.JSONDecodeError, KeyError):
        return False, None, None


def _parse_ical_datetime(value: str) -> Optional[datetime]:
    if not value:
        return None
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    if len(value) == 8 and value.isdigit():
        value = f"{value[:4]}-{value[4:6]}-{value[6:8]}T00:00:00+00:00"
    try:
        return get_datetime_utc(value)
    except (ValueError, TypeError):
        return None


def _ical_unfold(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith((" ", "\t")) and lines:
            lines[-1] += line[1:]
        else:
            lines.append(line)
    return "\n".join(lines)


def _parse_ical_events(ical_text: str, email_address: str) -> Tuple[Calendar, CalendarEvents]:
    calendar = Calendar()
    calendar.id = email_address
    calendar.summary = email_address

    events = CalendarEvents()
    unfolded = _ical_unfold(ical_text)
    for block in unfolded.split("BEGIN:VEVENT")[1:]:
        if "END:VEVENT" not in block:
            continue
        chunk = block.split("END:VEVENT", 1)[0]
        fields: Dict[str, str] = {}
        for line in chunk.splitlines():
            if ":" not in line:
                continue
            key, _, val = line.partition(":")
            fields[key.split(";", 1)[0].upper()] = val.strip()

        event = CalendarEvent()
        event.summary = fields.get("SUMMARY", "")
        event.location = fields.get("LOCATION", "")
        start = _parse_ical_datetime(fields.get("DTSTART", ""))
        end = _parse_ical_datetime(fields.get("DTEND", ""))
        if start:
            event.start.date_time = start
        if end:
            event.end.date_time = end
        event.creator.email = email_address
        events.items.append(event)

    return calendar, events


async def _fetch_public_via_ical(
    as_client: httpx.AsyncClient, email_address: str
) -> Tuple[bool, Optional[Calendar], Optional[CalendarEvents]]:
    """Fallback: published public iCal feed (no Google session required)."""
    ical_url = (
        f"https://calendar.google.com/calendar/ical/"
        f"{quote(email_address, safe='')}/public/basic.ics"
    )
    try:
        resp = await as_client.get(
            ical_url,
            follow_redirects=True,
            timeout=30.0,
            headers={"User-Agent": "Mozilla/5.0 (compatible; GHunt/2.x)"},
        )
        if resp.status_code != 200:
            return False, None, None
        body = resp.text
        if "BEGIN:VCALENDAR" not in body or "BEGIN:VEVENT" not in body:
            return False, None, None
        calendar, events = _parse_ical_events(body, email_address)
        return True, calendar, events
    except (httpx.HTTPError, ValueError):
        return False, None, None


async def fetch_all(
    ghunt_creds: GHuntCreds, as_client: httpx.AsyncClient, email_address: str
) -> Tuple[bool, Optional[Calendar], Optional[CalendarEvents]]:
    """
    Fetch a target's public Google Calendar.
    1) Authenticated Calendar API (requires GHunt login)
    2) Public API key (calendar published to the web)
    3) Public iCal feed
    """
    calendar_api = CalendarHttp(ghunt_creds)
    found, calendar = await calendar_api.get_calendar(as_client, email_address)
    source = "session"

    if not found:
        found, calendar, events = await _fetch_public_via_api_key(as_client, email_address)
        source = "public_api"
        if not found:
            found, calendar, events = await _fetch_public_via_ical(as_client, email_address)
            source = "public_ical"
        if not found:
            return False, None, None
    else:
        tmprinter = TMPrinter()
        _, events = await calendar_api.get_events(
            as_client, email_address, params_template="max_from_beginning"
        )
        next_page_token = deepcopy(events.next_page_token)
        while next_page_token:
            tmprinter.out(f"[~] Dumped {len(events.items)} events...")
            _, new_events = await calendar_api.get_events(
                as_client,
                email_address,
                params_template="max_from_beginning",
                page_token=next_page_token,
            )
            events.items += new_events.items
            next_page_token = deepcopy(new_events.next_page_token)
        tmprinter.clear()

    if calendar is not None:
        calendar._fetch_source = source  # type: ignore[attr-defined]
    return True, calendar, events


def public_calendar_links(email_address: str) -> Dict[str, str]:
    enc = quote(email_address, safe="")
    return {
        "ical": f"https://calendar.google.com/calendar/ical/{enc}/public/basic.ics",
        "embed": f"https://calendar.google.com/calendar/embed?src={enc}",
        "html": f"https://calendar.google.com/calendar/u/0/htmlembed?src={enc}",
        "share_settings": "https://calendar.google.com/calendar/u/0/r/settings/share",
    }


def out(
    calendar: Calendar,
    events: CalendarEvents,
    email_address: str,
    display_name: str = "",
    limit: int = 5,
):
    """Output fetched calendar events. If limit = 0, all events are shown."""

    source = getattr(calendar, "_fetch_source", "session")
    if source == "public_api":
        print("[~] Loaded via public Calendar API (no extra login beyond GHunt session for People API).\n")
    elif source == "public_ical":
        print("[~] Loaded via public iCal feed.\n")

    print(f"Calendar ID : {calendar.id}")
    if calendar.summary and calendar.summary != calendar.id:
        print(f"[+] Calendar Summary : {calendar.summary}")
    if calendar.time_zone:
        print(f"Calendar Timezone : {calendar.time_zone}")
    if getattr(events, "access_role", None):
        print(f"Access role : {events.access_role}")
    print()

    target_events = events.items[-limit:] if limit else events.items
    if target_events:
        total = len(events.items)
        shown = len(target_events)
        print(
            f"[+] {total} event{'s' if total != 1 else ''} dumped ! "
            f"Showing the last {shown} one{'s' if shown != 1 else ''}...\n"
        )

        table = BeautifulTable()
        table.set_style(BeautifulTable.STYLE_GRID)
        table.columns.header = ["Name", "Datetime (UTC)", "Duration"]

        for event in target_events:
            title = event.summary or "/"
            duration = "?"
            if event.end.date_time and event.start.date_time:
                duration = relativedelta(event.end.date_time, event.start.date_time)
                if duration.days or duration.hours or duration.minutes:
                    duration = (
                        f"{(str(duration.days) + ' day' + ('s' if duration.days > 1 else '')) if duration.days else ''} "
                        f"{(str(duration.hours) + ' hour' + ('s' if duration.hours > 1 else '')) if duration.hours else ''} "
                        f"{(str(duration.minutes) + ' minute' + ('s' if duration.minutes > 1 else '')) if duration.minutes else ''}"
                    ).strip()

            date = "?"
            if event.start.date_time:
                date = event.start.date_time.strftime("%Y/%m/%d %H:%M:%S")
            table.rows.append([title, date, duration])

        print(table)

        links = public_calendar_links(email_address)
        print("\n🗃️ Public calendar links :")
        print(f"=> iCal  : {links['ical']}")
        print(f"=> Embed : {links['embed']}")
        print(f"=> HTML  : {links['html']}")
    else:
        print("[-] No events dumped (calendar exists but has no events in range).")

    names = set()
    for event in events.items:
        if event.creator.email == email_address and (name := event.creator.display_name):
            if name != display_name:
                names.add(name)
    if names:
        print("\n[+] Found other names used by the target :")
        for name in names:
            print(f"- {name}")
