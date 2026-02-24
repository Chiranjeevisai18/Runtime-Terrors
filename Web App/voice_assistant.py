"""
Voice Assistant for Gruha Alankara.
Provides AI-powered interior design advice using Google Gemini 2.5 Flash
and gTTS for text-to-speech audio output.
"""

import os
import uuid
import traceback

# Directory to store generated audio files
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'static', 'audio')

# ── System prompt ────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert interior designer AI assistant for the Gruha Alankara platform — an AI & 3D Interior Design tool.

Your responsibilities:
1. ROOM LAYOUTS — How to arrange furniture for optimal flow and functionality.
2. COLOR SCHEMES — Color theory, mood effects of colors in different rooms.
3. LIGHTING — Natural and artificial lighting strategies.
4. STYLE GUIDES — Modern, Minimalist, Traditional, Industrial, Scandinavian, Bohemian, etc.
5. SPACE OPTIMIZATION — Making small rooms feel larger.
6. FURNITURE SELECTION — Choosing pieces that fit room size and style.
7. DECOR TIPS — Plants, artwork, rugs, accessories.

Guidelines:
- Keep answers concise (3-5 sentences).
- Be friendly, practical, and give specific actionable tips.
- If the user mentions a room type or style, tailor your advice accordingly.
- You may use emoji sparingly to keep the tone warm.
"""


def _ensure_audio_dir():
    """Create audio output directory if it doesn't exist."""
    os.makedirs(AUDIO_DIR, exist_ok=True)


# ── Public entry point ─────────────────────────────────────

def get_design_advice(query):
    """
    Generate interior design advice based on user query.
    Uses Google Gemini 2.5 Flash for text generation and optionally gTTS for speech.
    """
    _ensure_audio_dir()

    print(f"[Voice Assistant] Received query: {query}")

    # ---- Generate text response via Gemini ----
    text_response = _generate_text_response(query)
    print(f"[Voice Assistant] Response: {text_response[:100]}...")

    # ---- Generate audio using gTTS ----
    audio_path = _generate_speech(text_response)

    return {
        'text': text_response,
        'audio_url': f'/static/audio/{os.path.basename(audio_path)}' if audio_path else None,
        'query': query
    }


def _generate_text_response(query):
    """
    Generate a text response using Google Gemini 2.5 Flash.
    Falls back to rule-based responses if the API call fails.
    """
    try:
        import google.generativeai as genai

        # Get API key – try Flask config, then env, then hardcoded
        api_key = None
        try:
            from flask import current_app
            api_key = current_app.config.get('GEMINI_API_KEY')
            print(f"[Voice Assistant] Got API key from Flask config: {api_key[:10]}...")
        except Exception:
            pass

        if not api_key:
            api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyAoAMrlVClmXE6ye_1kr6X8Ey5jix9ckQY')
            print(f"[Voice Assistant] Using fallback API key: {api_key[:10]}...")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        full_prompt = f"{SYSTEM_PROMPT}\n\nUser question: {query}"
        print("[Voice Assistant] Calling Gemini API...")
        response = model.generate_content(full_prompt)
        print(f"[Voice Assistant] Gemini raw response received")

        text = response.text.strip()
        if text:
            return text

    except Exception as e:
        print(f"[Voice Assistant] Gemini API call failed:")
        traceback.print_exc()

    # Fall back to rule-based responses
    print("[Voice Assistant] Falling back to rule-based response")
    return _fallback_response(query)


# ── Fallback (keyword-based) ─────────────────────────────────

def _fallback_response(query):
    """
    Provide rule-based responses when Gemini API is unavailable.
    """
    query_lower = query.lower()

    tips = {
        'color': "For a harmonious look, use the 60-30-10 rule: 60% dominant color, 30% secondary, and 10% accent. Warm colors make rooms feel cozy, while cool tones create a calming atmosphere. 🎨",
        'small room': "To make a small room feel larger, use light colors on walls, add mirrors to reflect light, choose multi-functional furniture, and keep the floor clear. Vertical stripes on walls can add height. ✨",
        'bedroom': "For a restful bedroom, place the bed as the focal point against the largest wall. Use soft, warm lighting and keep electronics minimal. Layer bedding with complementary textures for a luxurious feel. 🛏️",
        'living room': "Arrange living room furniture to create conversation areas. Place the sofa facing the main entry point, add a coffee table within arm's reach, and ensure walkways are at least 3 feet wide. 🛋️",
        'kitchen': "In the kitchen, follow the work triangle principle: position the sink, stove, and refrigerator in a triangle for efficient movement. Add under-cabinet lighting for better task visibility. 🍳",
        'lighting': "Layer your lighting with three types: ambient (overhead), task (desk/reading lamps), and accent (decorative). Dimmer switches add versatility. Natural light should be maximized wherever possible. 💡",
        'modern': "Modern design emphasizes clean lines and minimal ornamentation. Choose furniture with simple geometric forms, use a neutral color palette with bold accents, and incorporate materials like glass, metal, and leather. 🏠",
        'minimalist': "Minimalist design follows 'less is more'. Keep only essential furniture, use white and neutral tones, maximize open space, and choose quality over quantity. Every piece should serve a purpose. ✨",
        'furniture': "When selecting furniture, measure your room first. Leave 18 inches between a coffee table and sofa. Ensure dining chairs have 24 inches of space each. Mix materials for visual interest. 🪑",
        'plant': "Indoor plants bring life to any room. Snake plants and pothos thrive in low light. Place taller plants in corners and smaller ones on shelves. Group plants in odd numbers for visual appeal. 🌿",
        'wall': "For walls, consider your room's natural light. North-facing rooms benefit from warm tones like soft yellows or warm whites. South-facing rooms can handle cooler shades. Accent walls in deeper colors add drama and depth! 🎨",
        'rug': "A rug should be large enough that at least the front legs of furniture rest on it. In living rooms, an 8x10 rug works for most layouts. Rugs add warmth, define spaces, and reduce noise. 🏠",
    }

    for keyword, tip in tips.items():
        if keyword in query_lower:
            return tip

    return "Great question! For personalized interior design advice, consider the room's purpose, natural lighting, and your personal style. Start with a focal point, then build the layout around it. Use the 3-color rule and mix textures for depth. 🎨"


# ── Text-to-Speech ───────────────────────────────────────────

def _generate_speech(text):
    """Convert text to speech using gTTS."""
    try:
        from gtts import gTTS

        filename = f"advice_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)

        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filepath)

        return filepath

    except Exception as e:
        print(f"[Voice Assistant] Speech generation failed: {e}")
        return None
