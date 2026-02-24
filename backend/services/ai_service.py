# Deferred imports for speed
# import torch
# from transformers import pipeline
import json
import re
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Model Singleton
class AIService:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AIService()
        return cls._instance

    def __init__(self):
        self.device = "cpu" # Default, updated in _init_models
        self.cache = {}
        self.gemini_model = None
        self.detr_pipe = None
        self.blip_pipe = None
        self._models_loaded = False
        
        # Init Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
            print("Gemini 2.5 Flash initialized")
        else:
            print("Warning: GEMINI_API_KEY not found in environment")
    
    def _init_models(self):
        if self._models_loaded:
            return
            
        print("Initializing Local AI Models (Lazy)...")
        try:
            import torch
            from transformers import pipeline
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # We keep local models for image analysis (DETR/BLIP)
            self.detr_pipe = pipeline("object-detection", model="facebook/detr-resnet-50", device=self.device)
            self.blip_pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base", device=self.device)
            self._models_loaded = True
            print(f"Local vision models loaded successfully on {self.device}")
        except Exception as e:
            print(f"Error loading models in AIService: {e}")

    def get_assistant_response(self, prompt):
        # Always try to get key lazily (pick up from env even if not set at init time)
        if not self.gemini_model:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                print("Gemini model lazily initialized from env.")
            else:
                return "I'm having trouble connecting to my brain. Please check the API key."
        
        if prompt in self.cache:
            return self.cache[prompt]
            
        try:
            # Request JSON structure specifically from Gemini
            response = self.gemini_model.generate_content(prompt)
            result_text = response.text
            
            if len(self.cache) > 100:
                self.cache.clear()
            self.cache[prompt] = result_text
            return result_text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return None

    def parse_json_response(self, raw_text):
        if not raw_text:
            return None
            
        try:
            # Gemini often wraps JSON in markdown blocks
            # Match code blocks first
            json_block_match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL)
            if json_block_match:
                return json.loads(json_block_match.group(1).strip())
            
            # Fallback to standard regex if no markdown blocks
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"JSON Parse Error: {e} for text: {raw_text}")
        return None

# Getter for blueprints
def get_ai_service():
    return AIService.get_instance()
