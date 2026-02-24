from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from .base_tool import format_tool_response

class QueryUserInput(BaseModel):
    question: str = Field(description="The exact question to ask the user, e.g., 'What color do you prefer, beige or grey?'.")
    context: str = Field(description="Why this information is needed.")

class QueryUserTool(BaseTool):
    name: str = "ask_user_for_info"
    description: str = "Use this tool ONLY when the checkout process is blocked because mandatory information is missing (like size, color, or shipping address). Pauses execution."
    args_schema: Type[BaseModel] = QueryUserInput

    def _run(self, question: str, context: str) -> str:
        # When the agent calls this, we want to bubble up an "INFO_REQUIRED" status
        # to the frontend. LangChain agents handle tool outputs. We return a specific
        # JSON string that our callback handler or main loop will catch and suspend the run.
        return format_tool_response("INFO_REQUIRED", "Suspending agent to ask user.", question=question, context=context)
