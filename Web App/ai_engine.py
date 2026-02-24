"""
AI Engine for Gruha Alankara.
Uses Hugging Face Transformers (DETR for object detection, BLIP for captioning)
to analyze uploaded room images and extract design-relevant information.
"""

import os
import json
import hashlib
from PIL import Image
from functools import lru_cache

# Global model references (lazy-loaded on first use)
_detector = None
_captioner = None
_detector_processor = None
_captioner_processor = None

# Cache directory for AI results
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'ai_cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# Furniture-related COCO labels that DETR can detect
FURNITURE_LABELS = {
    'couch', 'sofa', 'bed', 'chair', 'dining table', 'table',
    'tv', 'laptop', 'book', 'clock', 'vase', 'potted plant',
    'refrigerator', 'oven', 'microwave', 'toaster', 'sink',
    'toilet', 'bench', 'backpack', 'handbag', 'suitcase',
    'bottle', 'wine glass', 'cup', 'bowl', 'lamp'
}

# Room type keywords mapping
ROOM_TYPE_KEYWORDS = {
    'bedroom': ['bed', 'pillow', 'blanket', 'mattress', 'nightstand', 'wardrobe', 'sleep'],
    'living_room': ['sofa', 'couch', 'tv', 'television', 'coffee table', 'rug', 'living'],
    'kitchen': ['oven', 'refrigerator', 'sink', 'microwave', 'stove', 'kitchen', 'cook'],
    'bathroom': ['toilet', 'sink', 'bathtub', 'shower', 'mirror', 'bath'],
    'dining_room': ['dining table', 'chair', 'dining', 'plate', 'meal'],
    'office': ['desk', 'laptop', 'computer', 'monitor', 'office', 'book', 'bookshelf'],
}


def _load_detector():
    """
    Lazy-load the DETR object detection model.
    DETR (DEtection TRansformer) from Facebook identifies objects in images.
    """
    global _detector, _detector_processor
    
    if _detector is None:
        try:
            from transformers import DetrImageProcessor, DetrForObjectDetection
            
            model_name = "facebook/detr-resnet-50"
            print(f"[AI Engine] Loading object detection model: {model_name}")
            
            _detector_processor = DetrImageProcessor.from_pretrained(model_name)
            _detector = DetrForObjectDetection.from_pretrained(model_name)
            
            print("[AI Engine] Object detection model loaded successfully.")
        except Exception as e:
            print(f"[AI Engine] Warning: Could not load DETR model: {e}")
            raise
    
    return _detector, _detector_processor


def _load_captioner():
    """
    Lazy-load the BLIP image captioning model.
    BLIP (Bootstrapping Language-Image Pre-training) generates text descriptions of images.
    """
    global _captioner, _captioner_processor
    
    if _captioner is None:
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            
            model_name = "Salesforce/blip-image-captioning-base"
            print(f"[AI Engine] Loading captioning model: {model_name}")
            
            _captioner_processor = BlipProcessor.from_pretrained(model_name)
            _captioner = BlipForConditionalGeneration.from_pretrained(model_name)
            
            print("[AI Engine] Captioning model loaded successfully.")
        except Exception as e:
            print(f"[AI Engine] Warning: Could not load BLIP model: {e}")
            raise
    
    return _captioner, _captioner_processor


def detect_objects(image_path, confidence_threshold=0.7):
    """
    Detect objects in an image using DETR model.
    
    Args:
        image_path: Path to the image file
        confidence_threshold: Minimum confidence score to include a detection
    
    Returns:
        List of detected object names relevant to interior design
    """
    try:
        import torch
        
        model, processor = _load_detector()
        
        # Open and resize image for performance
        image = Image.open(image_path).convert('RGB')
        image = image.resize((800, 600))
        
        # Run detection
        inputs = processor(images=image, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Process results
        target_sizes = torch.tensor([image.size[::-1]])
        results = processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=confidence_threshold
        )[0]
        
        # Extract labels
        detected = []
        for score, label in zip(results["scores"], results["labels"]):
            label_name = model.config.id2label[label.item()].lower()
            if label_name not in detected:
                detected.append(label_name)
        
        return detected
    
    except Exception as e:
        print(f"[AI Engine] Object detection failed: {e}")
        return []


def generate_caption(image_path):
    """
    Generate a text description of the room image using BLIP.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        String caption describing the image
    """
    try:
        import torch
        
        model, processor = _load_captioner()
        
        # Open and resize image
        image = Image.open(image_path).convert('RGB')
        image = image.resize((384, 384))
        
        # Generate caption
        inputs = processor(image, return_tensors="pt")
        
        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=50)
        
        caption = processor.decode(output[0], skip_special_tokens=True)
        return caption
    
    except Exception as e:
        print(f"[AI Engine] Caption generation failed: {e}")
        return "A room interior"


def classify_room(detected_objects, caption, user_room_type=None):
    """
    Determine the room type based on detected objects, caption, and user input.
    User's selection takes priority, but AI validates or supplements it.
    
    Args:
        detected_objects: List of detected object names
        caption: Generated image caption
        user_room_type: Room type selected by the user
    
    Returns:
        String room type classification
    """
    if user_room_type and user_room_type != 'auto':
        return user_room_type
    
    # Score each room type
    scores = {}
    all_text = ' '.join(detected_objects) + ' ' + caption.lower()
    
    for room_type, keywords in ROOM_TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in all_text)
        scores[room_type] = score
    
    # Return highest scoring room type, default to living_room
    if scores:
        best = max(scores, key=scores.get)
        if scores[best] > 0:
            return best
    
    return 'living_room'


def _get_image_hash(image_path):
    """Generate hash of image file for caching."""
    with open(image_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def _get_cached_result(image_path, room_type, style):
    """Try to load cached AI analysis result."""
    try:
        image_hash = _get_image_hash(image_path)
        cache_key = f"{image_hash}_{room_type}_{style}"
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                print(f"[AI Engine] Using cached result for {image_path}")
                return json.load(f)
    except Exception as e:
        print(f"[AI Engine] Cache read error: {e}")
    return None


def _save_cached_result(image_path, room_type, style, result):
    """Save AI analysis result to cache."""
    try:
        image_hash = _get_image_hash(image_path)
        cache_key = f"{image_hash}_{room_type}_{style}"
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        
        with open(cache_file, 'w') as f:
            json.dump(result, f)
        print(f"[AI Engine] Cached result saved")
    except Exception as e:
        print(f"[AI Engine] Cache write error: {e}")


def analyze_room(image_paths, room_type='auto', style='modern'):
    """
    Main AI analysis function. Handles one or multiple images for a holistic room view.
    Now enhanced with Gemini 2.5 Flash for multi-angle contextual advice.
    
    Args:
        image_paths: List of paths (or single string path) to the uploaded room images
        room_type: User-selected room type (or 'auto' for AI detection)
        style: User-selected design style
    """
    if isinstance(image_paths, str):
        image_paths = [image_paths]
        
    print(f"[AI Engine] Analyzing {len(image_paths)} room images: {image_paths}")
    
    # Use first image as cache key for simplicity, but consider all in cache if needed
    primary_path = image_paths[0]
    cached = _get_cached_result(primary_path, room_type, style)
    if cached:
        return cached
    
    # default room type
    final_room_type = room_type if room_type != 'auto' else 'living_room'
    
    # ---- Step 1: Local Grounding Analysis (DETR + BLIP) ----
    print(f"[AI Engine] Running local grounding analysis on {len(image_paths)} images...")
    all_detected_objects = []
    all_captions = []
    images = []

    for path in image_paths:
        try:
            # Load image for processing
            img = Image.open(path)
            images.append(img)
            
            # DETR Object Detection
            objs = detect_objects(path)
            all_detected_objects.extend(objs)
            
            # BLIP Captioning
            cap = generate_caption(path)
            all_captions.append(f"View from {os.path.basename(path)}: {cap}")
            
        except Exception as e:
            print(f"[AI Engine] Local analysis error for {path}: {e}")

    # Deduplicate objects
    unique_objects = list(set(all_detected_objects))
    objects_context = ", ".join(unique_objects) if unique_objects else "No specific objects identified yet."
    captions_context = "\n".join(all_captions)

    # ---- Step 2: Gemini Analysis with Grounded Context ----
    try:
        import google.generativeai as genai
        from flask import current_app
        
        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyAoAMrlVClmXE6ye_1kr6X8Ey5jix9ckQY')
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        if not images:
            raise ValueError("No valid images successfully loaded for analysis")

        prompt = f"""Analyze these room images for a holistic interior design plan.
        
[GROUNDED INFORMATION FROM LOCAL MODELS]
- Identified Objects: {objects_context}
- Visual Descriptions:
{captions_context}

[USER PREFERENCES]
- Room Type Requested: {room_type}
- Desired Style: {style}

[CRITICAL] When recommending furniture, you MUST use ONLY these exact type keys:
sofa, table, chair, bed, wardrobe, bookshelf, lamp, desk, rug, tv_stand, dining_table, side_table, plant, mirror

Do NOT use variations like "coffee table" (use "table"), "floor lamp" (use "lamp"), 
"nightstand" (use "side_table"), "armchair" (use "chair"), etc.
        
Provide a comprehensive analysis in JSON format with the following keys:
- room_type: The confirmed room type based on the context and images.
- style_detected: Describe the current style.
- holistic_view: Summary of the entire room architecture and flow across all walls.
- pattern_analysis: Describe wall patterns or architectural features found.
- objects_detected: A list of existing items found.
- recommended_furniture: A list using ONLY the exact type keys above (e.g., ["sofa", "table", "lamp", "rug"]).
- placement_recommendations: A list of objects with:
    "item": (MUST be one of the exact type keys above, e.g., "sofa", "table", "lamp"),
    "where": (Specific location AND direction),
    "color": (a hex code to match suggested palette),
    "color_logic": (Explanation of matching relative to room patterns),
    "why": (a brief design reason),
    "description": (furniture type, material, look)
- color_palette: A list of 5 hex color codes.
- color_palette_explanation: Summary of why this overall color pattern was chosen.
- summary: A 2-sentence design summary.
"""
        
        print(f"[AI Engine] Calling Gemini Flash with {len(images)} images and grounded prompt...")
        response = model.generate_content([prompt] + images)
        
        # Parse JSON from response
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        else:
            import re
            match = re.search(r'(\{.*\})', text, re.DOTALL)
            if match:
                text = match.group(1)
            
        ai_data = json.loads(text)
        
        result = {
            'room_type': ai_data.get('room_type', final_room_type),
            'detected_objects': ai_data.get('objects_detected', unique_objects),
            'caption': ai_data.get('summary', "A curated design for your space."),
            'suggested_style': style,
            'recommended_furniture': ai_data.get('recommended_furniture', []),
            'color_scheme': ai_data.get('color_palette', []),
            'color_palette_explanation': ai_data.get('color_palette_explanation', ""),
            'detailed_placements': ai_data.get('placement_recommendations', []),
            'placement_suggestions': ai_data.get('summary', ""),
            'holistic_view': ai_data.get('holistic_view', "")
        }
        
        # Cache and return
        _save_cached_result(primary_path, room_type, style, result)
        print(f"[AI Engine] Multi-stage analysis successful.")
        return result
        
    except Exception as e:
        print(f"[AI Engine] Gemini stage failed: {e}")
    
    # Step 1: Detect objects (Fallback)
    detected_objects = detect_objects(primary_path)
    
    # Step 2: Generate caption (Fallback)
    caption = generate_caption(primary_path)
    
    # Step 3: Classify room type (Fallback)
    final_room_type = classify_room(detected_objects, caption, room_type)
    
    # Step 4: Build result
    result = {
        'room_type': final_room_type,
        'detected_objects': detected_objects,
        'caption': caption,
        'suggested_style': style,
        'recommended_furniture': ['sofa', 'rug', 'coffee_table', 'floor_lamp'],
        'color_scheme': ['#1a1a2e', '#16213e', '#0f3460', '#e94560', '#0f1428'],
        'detailed_placements': [
            {
                "item": "Sofa", 
                "where": "Central wall", 
                "color": "#1a1a2e",
                "why": "To create a focal point in the room.",
                "description": "A deep navy velvet sofa with modern clean lines and wooden legs."
            },
            {
                "item": "Rug", 
                "where": "Center floor", 
                "color": "#e94560",
                "why": "To anchor the seating area.",
                "description": "A high-pile geometric rug with accents of crimson and charcoal."
            }
        ],
        'placement_suggestions': f"Based on the analysis, this appears to be a {final_room_type.replace('_', ' ')}. Recommended style: {style}."
    }
    
    # Cache the result
    _save_cached_result(primary_path, room_type, style, result)
    
    return result
