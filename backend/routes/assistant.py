import json
import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.ai_service import get_ai_service

assistant_bp = Blueprint("assistant", __name__, url_prefix="/api/assistant")

@assistant_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    ai_service = get_ai_service()
    
    # We no longer need assistant_pipe check here as Gemini is a cloud API
    # But lazy-init local vision models if they'll be used for context (future)
    if not ai_service._models_loaded:
        ai_service._init_models()

    data = request.get_json()
    if not data or 'user_message' not in data:
        return jsonify({"message": "user_message is required"}), 400

    user_message = data.get('user_message')
    context_id = data.get('context_id') # Phase 8 enhancement
    
    # Fallbacks in case context_id isn't provided or found
    room_type = data.get('room_type', 'unknown')
    current_furniture = data.get('current_furniture', [])
    style_theme = data.get('style_theme', 'modern')
    
    # Override with rich context if available
    from routes.ai import ai_context_store
    if context_id and context_id in ai_context_store:
        ctx = ai_context_store[context_id]
        room_type = ctx.get("room_type", room_type)
        style_theme = ctx.get("style", style_theme)
        # Append detected objects to current furniture
        detected = ctx.get("detected_objects", [])
        if detected:
            current_furniture = list(set(current_furniture + detected))

    # Advanced prompt for Gemini
    prompt = f"""
    You are 'Alankara AI', a world-class interior designer. Give helpful, professional, and friendly advice.
    
    CONTEXT (Remember this from the user's room scan):
    - Room Type: {room_type}
    - Style Theme: {style_theme}
    - Detailed Objects in Room: {', '.join(current_furniture) if current_furniture else 'Empty'}
    
    USER QUERY: "{user_message}"
    
    TASK:
    1. Provide advice using beautiful Markdown (use bold, italics, and bullet points).
    2. Be specific to the room type and style provided.
    3. Respond ONLY in the following JSON format:
    {{
      "text": "Your markdown-formatted response here",
      "suggested_action": "none | remove_object | add_item | change_color"
    }}
    
    If you suggest adding an item, set suggested_action to 'add_item'.
    """
    
    try:
        raw_text = ai_service.get_assistant_response(prompt)
        if not raw_text:
            raise ValueError("Empty response from AI")
            
        print(f"Assistant Raw Output: {raw_text}")
        response_data = ai_service.parse_json_response(raw_text)
        
        if not response_data:
            # Emergency extraction if JSON is wrapped in text
            response_data = {
                "text": raw_text.strip(),
                "suggested_action": "none"
            }
            
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error in assistant chat: {e}")
        return jsonify({
            "text": "I'm having a brief creative block. Could you try rephrasing that?",
            "suggested_action": "none"
        }), 200
