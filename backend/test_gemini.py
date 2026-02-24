from services.ai_service import get_ai_service
import json

def test_gemini_integration():
    print("Testing Gemini 2.5 Flash Integration...")
    ai_service = get_ai_service()
    
    test_prompt = """
    You are 'Alankara AI', a world-class interior designer.
    CONTEXT:
    - Room Type: bedroom
    - Style Theme: Modern
    - Current Items in Room: bed, nightstand
    
    USER QUERY: "Suggest a good color for the walls."
    
    TASK:
    1. Provide advice using Markdown.
    2. Respond ONLY in the following JSON format:
    {
      "text": "Your markdown-formatted response here",
      "suggested_action": "none | remove_object | add_item | change_color"
    }
    """
    
    print("\nSending prompt to Gemini...")
    raw_response = ai_service.get_assistant_response(test_prompt)
    
    if raw_response:
        print("\n--- RAW RESPONSE ---")
        print(raw_response)
        
        print("\n--- PARSED JSON ---")
        parsed = ai_service.parse_json_response(raw_response)
        if parsed:
            print(json.dumps(parsed, indent=2))
            print("\nVerification: SUCCESS!")
        else:
            print("Verification: FAILED to parse JSON.")
    else:
        print("Verification: FAILED - Empty response.")

if __name__ == "__main__":
    test_gemini_integration()
