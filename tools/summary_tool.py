import json
import logging
import os
from typing import Any, Dict, Optional

from openai import OpenAI

from tools.calendar_tool import get_events
from tools.expense_tool import analyze_expenses
from tools.todo_tool import handle_todo
from tools.weather_tool import get_weather

logger = logging.getLogger(__name__)

DEFAULT_CITY = os.getenv("SMART_LIFE_DEFAULT_CITY", "Bengaluru")
DEFAULT_MODEL = os.getenv("SMART_LIFE_OPENAI_MODEL", "gpt-4o-mini")


def _load_openai_client() -> Optional[OpenAI]:
    """Return an OpenAI client when configured, otherwise None."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY environment variable is not set; using fallback summary.")
        return None

    try:
        return OpenAI(api_key=api_key)
    except Exception:  # pragma: no cover - defensive guard
        logger.exception("Unable to initialise OpenAI client.")
        return None


def _collect_context() -> Dict[str, Any]:
    """Gather raw data from the individual tools, tolerating errors."""
    context: Dict[str, Any] = {}

    for label, producer in (
        ("events", lambda: get_events()),
        ("expenses", analyze_expenses),
        ("weather", lambda: get_weather(DEFAULT_CITY)),
        ("todos", lambda: handle_todo("list")),
    ):
        try:
            context[label] = producer()
        except Exception as exc:  # pragma: no cover - resilience path
            logger.exception("Failed to collect %s data", label)
            context[label] = {"error": str(exc)}

    return context


def _format_fallback_summary(context: Dict[str, Any]) -> str:
    """Generate a lightweight summary when LLM access is unavailable."""
    events = context.get("events", {})
    weather_info = context.get("weather", {})
    expenses = context.get("expenses", {})
    todos = context.get("todos", {})

    lines = ["Smart Life Daily Snapshot:"]

    if isinstance(weather_info, dict) and "city" in weather_info:
        lines.append(f"- Weather in {weather_info['city']}: {weather_info.get('temp', '?')}°C, {weather_info.get('description', 'n/a')}")

    if isinstance(events, dict) and events.get("events"):
        lines.append(f"- {len(events['events'])} event(s) scheduled for {events.get('date', 'today')}.")
    elif isinstance(events, dict) and events.get("message"):
        lines.append(f"- Events: {events['message']}")

    if isinstance(expenses, dict) and expenses.get("total") is not None:
        lines.append(f"- Expenses total: INR {expenses['total']:.2f} across {len(expenses.get('by_category', {}))} category(ies).")

    if isinstance(todos, dict):
        todos_list = todos.get("todos")
        if todos_list:
            pending = [item for item in todos_list if not item.get("done")]
            lines.append(f"- Todos pending: {len(pending)}/{len(todos_list)}")
        elif todos.get("message"):
            lines.append(f"- Todos: {todos['message']}")

    return "\n".join(lines)


def summarize_day() -> Dict[str, Any]:
    """Produce a natural language summary of the day."""
    context = _collect_context()

    client = _load_openai_client()
    if not client:
        return {
            "summary": _format_fallback_summary(context),
            "model": None,
            "context": context,
        }

    prompt = (
        "Create a concise daily summary combining the calendar, weather, expenses, and to-do data.\n"
        "Highlight significant items and provide an encouraging close."
    )

    context_json = json.dumps(context, default=str, indent=2)

    try:
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful lifestyle assistant."},
                {"role": "user", "content": f"{prompt}\n\nContext:\n{context_json}"},
            ],
        )
        message = completion.choices[0].message
        summary_text = getattr(message, "content", None) or message.get("content")
    except Exception as exc:  # pragma: no cover - network/API failures
        logger.exception("Failed to generate summary with OpenAI: %s", exc)
        return {
            "summary": _format_fallback_summary(context),
            "model": None,
            "context": context,
            "error": str(exc),
        }

    return {
        "summary": summary_text.strip() if isinstance(summary_text, str) else summary_text,
        "model": DEFAULT_MODEL,
        "context": context,
    }
