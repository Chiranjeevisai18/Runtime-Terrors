
import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
import sys

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key

# --- MOCK SCRAPER / AGENT SERVICES ---
from services.product_scraper import search_amazon_products

@tool("find")
def find_tool(query: str) -> str:
    """Search for furniture products. Returns JSON list."""
    print(f"\n[TOOL CALLED]: Searching Amazon for '{query}'...")
    results = search_amazon_products(query)
    return json.dumps(results)

@tool("cart")
def cart_tool(url: str) -> str:
    """Add product to cart using its URL."""
    print(f"\n[TOOL CALLED]: Adding {url} to cart...")
    return json.dumps({"status": "SUCCESS", "message": "Added to cart."})

@tool("ask")
def ask_tool(question: str) -> str:
    """Ask the user a question if information is missing."""
    print(f"\n[AGENT ASK]: {question}")
    # Simulating a pause where we would return to the user
    return json.dumps({"status": "INFO_REQUIRED", "question": question})

@tool("buy")
def buy_tool(product_url: str) -> str:
    """Finish the purchase. Triggers secure handoff if needed."""
    print(f"\n[TOOL CALLED]: Buying {product_url}...")
    return json.dumps({"status": "FALLBACK", "reason": "SECURE_HANDOFF_REQUIRED"})

# Initialize LLM & Tools
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)
tools = [find_tool, cart_tool, ask_tool, buy_tool]
llm_with_tools = llm.bind_tools(tools)
tool_map = {t.name: t for t in tools}

def run_chat_turn(messages):
    print("\n--- Agent is thinking ---")
    response = llm_with_tools.invoke(messages)
    messages.append(response)
    
    if not response.tool_calls:
        print(f"\n[AGENT RESPONSE]: {response.content}")
        return messages, False
        
    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        print(f"Action: {tool_name} with {tool_args}")
        
        tool_func = tool_map.get(tool_name)
        if tool_func:
            result = tool_func.invoke(tool_args)
        else:
            result = f"Error: Tool {tool_name} not found."
            
        messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"],
            name=tool_name
        ))
    return messages, True

print("=== STARTING AGENT CONVERSATION TEST ===")
messages = [
    HumanMessage(content="You are a shopping assistant. Help me find and buy things. Use your tools to find items, ask me questions if you need to know which one I want, then buy the one I choose.")
]

# Turn 1: User says fetch
print("\n[USER]: Can you find me some modern lamps?")
messages.append(HumanMessage(content="Can you find me some modern lamps?"))
messages, had_tools = run_chat_turn(messages)

# Let agent process the tool result
if had_tools:
    messages, _ = run_chat_turn(messages)

# Turn 2: User answers the agent selection question
print("\n[USER]: The premium one sounds good. Buy it.")
messages.append(HumanMessage(content="The premium one sounds good. Buy it."))
messages, had_tools = run_chat_turn(messages)

if had_tools:
    messages, _ = run_chat_turn(messages)

print("\n=== TEST FINISHED ===")

