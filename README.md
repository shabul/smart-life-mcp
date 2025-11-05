# Smart Life Dashboard MCP

Smart Life Dashboard MCP is a showcase project that turns local life-log data into a set of composable [Model Context Protocol](https://github.com/modelcontextprotocol) tools. It wraps calendar events, expenses, weather data, to-dos, and daily summaries behind a single FastMCP server so you can integrate them with LLM clients or MCP tooling hubs.

## Features

- **Calendar:** list and append events stored in `data/events.json`.
- **Weather:** fetch current conditions from OpenWeather for any city.
- **Expenses:** analyse spending totals and category breakdowns from CSV data.
- **To-dos:** list, add, and complete personal tasks stored in JSON.
- **Daily summary:** combine all datasets into a natural language briefing with OpenAI (includes an offline fallback).
- **Python exec (demo):** run small, sandboxed Python snippets for explorations.

## Project structure

```
smart-life-mcp/
    data/
        events.json
        expenses.csv
        todo.json
    tools/
        calendar_tool.py
        expense_tool.py
        python_exec_tool.py
        summary_tool.py
        todo_tool.py
        weather_tool.py
    main.py
    requirements.txt
```

## Getting started

1. **Create and activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables**
   Copy `.env.example` to `.env` (or export the variables manually) and provide your API keys.

4. **Run the MCP server**
   ```bash
   python main.py
   ```
   By default the server starts on port `8000`. Override with `SMART_LIFE_PORT`.

## Environment variables

| Name | Required | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | Optional\* | Enables LLM powered daily summaries. Without it, a fallback summary is used. |
| `OPENWEATHER_API_KEY` | Yes | Required for `weather` tool responses from OpenWeather. |
| `SMART_LIFE_PORT` | No | HTTP port for the MCP server (default `8000`). |
| `SMART_LIFE_DEFAULT_CITY` | No | Default city for weather lookups (default `Bengaluru`). |
| `SMART_LIFE_OPENAI_MODEL` | No | Chat completion model name (default `gpt-4o-mini`). |
| `SMART_LIFE_LOG_LEVEL` | No | Logging level, e.g. `INFO`, `DEBUG`. |

\*Daily summaries fall back to a lightweight on-device report when `OPENAI_API_KEY` is absent or the API call fails.

## Available tools

| Tool name | Arguments | Purpose |
| --- | --- | --- |
| `calendar` | `date` (optional `YYYY-MM-DD`) | Retrieve events for today or a specific date. |
| `add-event` | `date`, `event`, `time?`, `location?` | Append a new calendar event to `events.json`. |
| `weather` | `city?` | Fetch current weather via OpenWeather. |
| `expenses` | — | Summarise spending totals and category breakdowns. |
| `todo` | `action` (`list`, `add`, `done`), `task?` | Manage your to-do list. |
| `summary` | — | Generate a daily wrap up combining all datasets. |
| `python_exec` | `code` | Execute short Python snippets with restricted built-ins. |

## Sample data

The `data/` directory ships with example JSON/CSV files so the project works out of the box. Replace them with your own data to personalise the dashboard. All tools expect UTF-8 encoded files.

## Development notes

- The project targets Python 3.10 or later.
- `python_exec_tool` is intentionally minimal and should never be exposed to untrusted input.
- When deploying to production, move secrets to a proper secret manager and consider persisting data in a database rather than flat files.

## License

Released under the MIT License. See `LICENSE` for details.
