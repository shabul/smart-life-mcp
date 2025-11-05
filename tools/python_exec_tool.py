import io
import contextlib

def run_python(code: str):
    """
    Safely executes small Python snippets and returns printed output.
    ⚠️ For hackathon/demo use only (no network or file ops).
    """

    # Capture stdout
    buffer = io.StringIO()
    restricted_globals = {
        "__builtins__": {
            "print": print,
            "range": range,
            "len": len,
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
            "sorted": sorted,
        }
    }

    try:
        with contextlib.redirect_stdout(buffer):
            exec(code, restricted_globals)
        result = buffer.getvalue().strip()
        return {"success": True, "output": result or "(no output)"}
    except Exception as e:
        return {"success": False, "error": str(e)}
