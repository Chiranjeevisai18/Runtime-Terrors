import json
from langchain_core.tools import BaseTool
from pydantic import Field
from typing import Optional, Type, Dict, Any

class PlaywrightToolException(Exception):
    """Exception raised by Playwright tools during automation."""
    pass

def format_tool_response(status: str, message: str, **kwargs) -> str:
    """Standardizes JSON output for the agent."""
    response = {
        "status": status,
        "message": message
    }
    response.update(kwargs)
    return json.dumps(response)
