import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)
EVENTS_PATH = Path(__file__).resolve().parent.parent / "data" / "events.json"


def get_events(date=None):
    """
    Reads local events.json and returns today's or all upcoming events.
    If date not provided, defaults to today.
    """

    if not EVENTS_PATH.exists():
        logger.error("Events data file missing at %s", EVENTS_PATH)
        return {"error": "events.json file not found"}

    try:
        with open(EVENTS_PATH, "r", encoding="utf-8") as f:
            events = json.load(f)
    except json.JSONDecodeError:
        logger.exception("Unable to parse events JSON at %s", EVENTS_PATH)
        return {"error": "events.json is not valid JSON"}

    # Default date = today
    today = date or datetime.now().strftime("%Y-%m-%d")
    logger.debug("Looking up events for %s", today)

    # Filter events for today
    today_events = [e for e in events if e["date"] == today]

    if not today_events:
        logger.info("No events found for %s in %s", today, EVENTS_PATH)
        return {"message": f"No events found for {today}"}

    logger.debug("Found %s events for %s", len(today_events), today)
    return {"date": today, "events": today_events}


def add_event(event_data):
    """
    Append a new event to events.json.
    Expects a dict with at least 'date' (YYYY-MM-DD) and 'event'.
    """

    if not isinstance(event_data, dict):
        logger.error("Event data must be a dict, received %s", type(event_data))
        return {"error": "event_data must be a dictionary"}

    missing_fields = [field for field in ("date", "event") if not event_data.get(field)]
    if missing_fields:
        logger.error(
            "Event data missing required fields %s: %s", missing_fields, event_data
        )
        return {"error": f"Missing required fields: {', '.join(missing_fields)}"}

    try:
        datetime.strptime(event_data["date"], "%Y-%m-%d")
    except ValueError:
        logger.error("Invalid date format for event: %s", event_data)
        return {"error": "date must be in YYYY-MM-DD format"}

    if not EVENTS_PATH.exists():
        logger.warning("Events file not found at %s; creating a new file.", EVENTS_PATH)
        EVENTS_PATH.write_text("[]", encoding="utf-8")

    try:
        with EVENTS_PATH.open("r", encoding="utf-8") as f:
            events = json.load(f)
    except json.JSONDecodeError:
        logger.exception("Unable to parse events JSON at %s; resetting file.", EVENTS_PATH)
        events = []

    events.append(event_data)

    with EVENTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)

    logger.info("Added new event on %s: %s", event_data["date"], event_data.get("event"))
    return {"message": "Event added successfully.", "event": event_data}
