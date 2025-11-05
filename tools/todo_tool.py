import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
TODO_PATH = Path(__file__).resolve().parent.parent / "data" / "todo.json"


def handle_todo(action="list", task=None):
    """
    Manage to-do list stored in data/todo.json.
    Supported actions:
      - 'list'          → list all tasks
      - 'add'           → add a new task
      - 'done'          → mark a task as done
    """

    if not TODO_PATH.exists():
        logger.warning("Todo data file missing at %s; creating a new file.", TODO_PATH)
        TODO_PATH.write_text("[]", encoding="utf-8")

    try:
        with TODO_PATH.open("r", encoding="utf-8") as f:
            todos = json.load(f)
    except json.JSONDecodeError:
        logger.exception("Unable to parse todo JSON at %s; resetting file.", TODO_PATH)
        todos = []
        TODO_PATH.write_text("[]", encoding="utf-8")

    logger.debug("Handling todo action=%s with task=%s", action, task)

    if action == "list":
        if not todos:
            logger.info("Todo list is empty in %s", TODO_PATH)
            return {"message": "No tasks found"}
        return {"todos": todos}

    if action == "add" and task:
        todos.append({"task": task, "done": False})
        with TODO_PATH.open("w", encoding="utf-8") as f:
            json.dump(todos, f, indent=2)
        logger.info("Added new task '%s' to %s", task, TODO_PATH)
        return {"message": f"Task '{task}' added successfully."}

    if action == "done" and task:
        for todo in todos:
            if todo["task"].lower() == task.lower():
                todo["done"] = True
                with TODO_PATH.open("w", encoding="utf-8") as f:
                    json.dump(todos, f, indent=2)
                logger.info("Marked task '%s' as done in %s", task, TODO_PATH)
                return {"message": f"Task '{task}' marked as done."}
        logger.warning("Requested task '%s' not found in %s", task, TODO_PATH)
        return {"error": f"Task '{task}' not found."}

    logger.error("Invalid todo action '%s' or missing task argument.", action)
    return {"error": "Invalid action or missing task name."}
