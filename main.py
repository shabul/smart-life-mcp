"""Smart Life Dashboard MCP server entrypoint."""

import logging
import os
from pathlib import Path
from typing import Dict, Optional

from fastmcp import FastMCP

from tools.calendar_tool import add_event, get_events
from tools.expense_tool import analyze_expenses
from tools.python_exec_tool import run_python
from tools.summary_tool import summarize_day
from tools.todo_tool import handle_todo
from tools.weather_tool import get_weather

logging.basicConfig(
    level=os.getenv("SMART_LIFE_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent / "data"
REQUIRED_DATA_FILES: Dict[str, Path] = {
    "expenses": DATA_DIR / "expenses.csv",
    "events": DATA_DIR / "events.json",
    "todo": DATA_DIR / "todo.json",
}

app = FastMCP(name="Smart Life Dashboard")


def _validate_data_files(required_files: Dict[str, Path]) -> None:
    """Log the availability of the local data files used by the tools."""
    for label, file_path in required_files.items():
        if file_path.exists():
            logger.info("Found %s data file at %s", label, file_path)
        else:
            logger.warning("Missing %s data file at %s", label, file_path)


@app.tool("calendar", description="Get calendar events for a given date (defaults to today).")
def calendar_tool(date: Optional[str] = None):
    """Return calendar events for today or for the provided YYYY-MM-DD date."""
    return get_events(date=date)


@app.tool("add-event", description="Add a calendar event to the local dataset.")
def add_event_tool(date: str, event: str, time: Optional[str] = None, location: Optional[str] = None):
    """Persist a new calendar event to the local events.json file."""
    event_data = {"date": date, "event": event}
    if time:
        event_data["time"] = time
    if location:
        event_data["location"] = location
    return add_event(event_data)


@app.tool("weather", description="Fetch the current weather for a city (OpenWeather).")
def weather_tool(city: str = "Bengaluru"):
    """Fetch weather information for the requested city."""
    return get_weather(city)


@app.tool("expenses", description="Analyze monthly expenses from CSV data.")
def expenses_tool():
    """Return a summary of expenses by category and the total."""
    return analyze_expenses()


@app.tool("todo", description="Manage the to-do list (actions: list, add, done).")
def todo_tool(action: str = "list", task: Optional[str] = None):
    """Interact with the todo list JSON file."""
    return handle_todo(action, task)


@app.tool("summary", description="Summarize the day using calendar, weather, expenses, and todos.")
def summary_tool():
    """Produce a natural language summary of the day's highlights."""
    return summarize_day()


@app.tool("python_exec", description="Execute small Python snippets in a restricted environment.")
def python_exec(code: str):
    """Execute short Python snippets and return their stdout."""
    return run_python(code)


def main() -> None:
    """Start the MCP server."""
    _validate_data_files(REQUIRED_DATA_FILES)
    port = int(os.getenv("SMART_LIFE_PORT", 8000))
    logger.info("Starting Smart Life Dashboard MCP server on port %s", port)
    app.run(transport="http", port=port)


if __name__ == "__main__":
    main()
