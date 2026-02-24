import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
from services.product_scraper import get_or_scrape_products

# --- TOOLS ---

@tool("find")
def find_tool(query: str) -> str:
    """Search for furniture products. Returns JSON list."""
    try:
         print(f"AGENT_TOOL: find({query})")
         results = get_or_scrape_products(query)
         return json.dumps(results)
    except Exception as e:
         return json.dumps({"status": "ERROR", "message": str(e)})

@tool("cart")
def cart_tool(url: str) -> str:
    """Add product to cart using its URL."""
    print(f"AGENT_TOOL: cart({url})")
    return json.dumps({"status": "SUCCESS", "message": "Added to cart."})

@tool("ask")
def ask_tool(question: str) -> str:
    """Ask the user a question if information is missing."""
    print(f"AGENT_TOOL: ask({question})")
    return json.dumps({"status": "INFO_REQUIRED", "question": question})

@tool("buy")
def buy_tool(product_url: str) -> str:
    """Finish the purchase. Triggers secure handoff if needed."""
    print(f"AGENT_TOOL: buy({product_url})")
    return json.dumps({"status": "FALLBACK", "reason": "SECURE_HANDOFF_REQUIRED"})

# --- MANUAL AGENT LOOP ---

def run_booking_agent(product_url: str, user_id: int):
    api_key = os.getenv("GEMINI_API_KEY")
    os.environ["GOOGLE_API_KEY"] = api_key
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.0)
    tools = [find_tool, cart_tool, ask_tool, buy_tool]
    llm_with_tools = llm.bind_tools(tools)
    
    messages = [
        HumanMessage(content=f"You are a shopping assistant. Buy this item: {product_url}. If it's a name, search for it. Use tools. Conclude with a JSON final answer: {{\"status\": \"...\", \"reason\": \"...\"}}")
    ]
    
    # Tool mapping for execution
    tool_map = {t.name: t for t in tools}
    
    # Limit turns to prevent tunnel timeouts (503)
    max_turns = 3
    for i in range(max_turns):
        print(f"AGENT_LOOP: Turn {i+1}")
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        
        if not response.tool_calls:
            # End of conversation
            break
            
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"AGENT_LOOP: Executing {tool_name}...")
            
            # Execute tool
            tool_func = tool_map.get(tool_name)
            if tool_func:
                result = tool_func.invoke(tool_args)
            else:
                result = f"Error: Tool {tool_name} not found."
                
            # Append ToolMessage with explicit name
            messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
                name=tool_name # Explicitly set name to avoid "empty name" error
            ))
            
    # Final response extraction
    final_text = messages[-1].content
    print(f"AGENT_FINAL: {final_text}")
    
    try:
        # Clean markdown if present
        if "```" in final_text:
            final_text = final_text.split("```")[1]
            if final_text.startswith("json"): final_text = final_text[4:]
        return json.loads(final_text.strip())
    except:
        return {"status": "FAILED", "reason": "Agent output was not valid JSON", "raw": final_text}
