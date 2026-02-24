from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from PIL import Image
import io
import torch
import numpy as np
import cv2
from sklearn.cluster import KMeans
from services.ai_service import get_ai_service

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")

# In-memory context store (For Phase 8 Context Sharing across Chat and Agents)
ai_context_store = {}

# Initialize models (singleton-like for the process)
# This block is removed as ai_service handles model initialization
# print("Loading AI models (DETR & BLIP)...")
# try:
#     # Set device to GPU if available
#     device = "cuda" if torch.cuda.is_available() else "cpu"
    
#     # Object detection model
#     detr_pipe = pipeline("object-detection", model="facebook/detr-resnet-50", device=device)
    
#     # Image captioning model
#     blip_pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base", device=device)
    
#     print(f"Models loaded successfully on {device}")
# except Exception as e:
#     print(f"Error loading models: {e}")
#     detr_pipe = None
#     blip_pipe = None

def map_objects_to_furniture(detected_objects):
    """Refined rule-based mapping from detected objects to the expanded 15+ asset library."""
    recommendations_map = {}
    
    # Map lowercase labels
    labels = [obj['label'].lower() for obj in detected_objects]
    
    def add_rec(model_id, name):
        if model_id not in recommendations_map:
            recommendations_map[model_id] = {"model_id": model_id, "name": name}

    for label in labels:
        # Seating
        if label in ['sofa', 'couch', 'living room']:
            add_rec("sheen_sofa_01", "Sheen Velvet Sofa")
        if label in ['chair', 'armchair', 'seat']:
            add_rec("accent_chair_01", "Sheen Accent Chair")
        
        # Tables & Workspace
        if label in ['dining table', 'table', 'desk']:
            add_rec("gaming_desk_01", "Gaming Desk & Set")
        if label in ['laptop', 'monitor', 'keyboard', 'mouse']:
            add_rec("pc_setup_01", "Modern PC Setup")
        
        # Lighting
        if label in ['lamp', 'light', 'lantern']:
            add_rec("lantern_01", "Antique Lantern")
        if label in ['candle', 'fire', 'lighting']:
            add_rec("candle_01", "Hurricane Candle")
            
        # Decor & Objects
        if label in ['camera', 'optics']:
            add_rec("camera_01", "Antique Camera")
        if label in ['bottle', 'cup', 'glass', 'drink']:
            add_rec("bottle_01", "Glass Water Bottle")
        if label in ['car', 'toy', 'vehicle']:
            add_rec("toy_car_01", "Vintage Toy Car")
        if label in ['plant', 'fruit', 'food']:
            add_rec("avocado_01", "Plush Avocado")
        if label in ['plate', 'bowl', 'dish']:
            add_rec("olives_01", "Olive Dish")
        if label in ['box', 'package', 'container']:
            add_rec("wooden_crate_01", "Rustic Crate")
        if label in ['backpack', 'bag', 'helmet']:
            add_rec("helmet_01", "Explorer Helmet")

    recommendations = list(recommendations_map.values())
        
    # Default fallbacks if nothing detected
    if not recommendations:
        recommendations.append({"model_id": "sheen_sofa_01", "name": "Sheen Velvet Sofa"})
        recommendations.append({"model_id": "accent_chair_01", "name": "Sheen Accent Chair"})
        recommendations.append({"model_id": "lantern_01", "name": "Antique Lantern"})
        
    return recommendations

def refine_recommendations(room_type, detected_objects, rule_recommendations, style):
    """LLM-based refinement for style consistency."""
    ai_service = get_ai_service()
    if not ai_service.gemini_model:
        # Fallback to rule-based if Gemini isn't available
        return rule_recommendations

    rec_names = [r['name'] for r in rule_recommendations]
    
    prompt = f"""
    You are an interior design expert.
    Context:
    Room Type: {room_type}
    Objects detected: {', '.join(detected_objects)}
    Style Theme: {style}
    Rule-based recommendations: {', '.join(rec_names)}

    Refine the recommendation list for style consistency.
    Only suggest items from the rule-based recommendation list.
    
    Respond ONLY in valid JSON format:
    {{
      "refined_recommendations": ["Item Name 1", "Item Name 2"]
    }}
    """
    
    try:
        raw_text = ai_service.get_assistant_response(prompt)
        response_data = ai_service.parse_json_response(raw_text)
        
        if response_data and "refined_recommendations" in response_data:
            refined_names = response_data["refined_recommendations"]
            # Map back to IDs
            final_recs = []
            for name in refined_names:
                for rule_rec in rule_recommendations:
                    if rule_rec['name'].lower() == name.lower():
                        final_recs.append(rule_rec)
                        break
            return final_recs if final_recs else rule_recommendations
    except Exception as e:
        print(f"Refinement error: {e}")
        
    return rule_recommendations

@ai_bp.route("/analyze-room", methods=["POST"])
@jwt_required()
def analyze_room():
    ai_service = get_ai_service()
    if not ai_service.detr_pipe or not ai_service.blip_pipe:
        print("Vision models not loaded. Attempting initialization...")
        ai_service._init_models()
        if not ai_service.detr_pipe or not ai_service.blip_pipe:
            print("Failed to initialize vision models.")
            return jsonify({"message": "AI models are still initializing or failed to load. Please try again in a few seconds."}), 503

    if 'image' not in request.files:
        return jsonify({"message": "No image provided"}), 400

    file = request.files['image']
    try:
        # Load image
        image_bytes = file.read()
        print(f"Received image: {len(image_bytes)} bytes")
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # 1. Image Captioning (BLIP)
        print("Running BLIP image captioning...")
        caption_result = ai_service.blip_pipe(image)
        description = caption_result[0]['generated_text'] if caption_result else "Unknown room"
        print(f"BLIP Caption: {description}")
        
        # 2. Object Detection (DETR)
        print("Running DETR object detection...")
        detr_results = ai_service.detr_pipe(image)
        
        # Log all detections for debugging
        for res in detr_results:
            print(f"Detected: {res['label']} (Score: {res['score']:.3f})")

        # Filter for high confidence objects (>0.6 - lowered from 0.8 for better recall)
        detected_objects = [
            {"label": res['label'], "score": round(res['score'], 3)}
            for res in detr_results if res['score'] > 0.6
        ]
        
        # 3. Infer Room Type
        room_type = "living_room"
        if "bedroom" in description.lower() or any(o['label'] == 'bed' for o in detected_objects):
            room_type = "bedroom"
        elif "kitchen" in description.lower() or any(o['label'] == 'dining table' for o in detected_objects):
            room_type = "kitchen"
        print(f"Inferred Room Type: {room_type}")
        
        # 4. Infer Style
        style = "Modern"
        if "minimal" in description.lower(): style = "Minimalist"
        elif "rustic" in description.lower(): style = "Rustic"

        # 5. Generate Recommendations
        print("Generating rule-based recommendations...")
        rule_recs = map_objects_to_furniture(detected_objects)
        print(f"Rule Recommendations: {[r['name'] for r in rule_recs]}")
        
        # 6. LLM Refinement
        print("Refining recommendations with Gemini...")
        try:
            refined_recs = refine_recommendations(
                room_type, 
                [obj['label'] for obj in detected_objects], 
                rule_recs, 
                style
            )
            print(f"Final Refined Recommendations: {[r['name'] for r in refined_recs]}")
        except Exception as llm_error:
            if "429" in str(llm_error) or "Exhausted" in str(llm_error) or "Resource exhausted" in str(llm_error):
                print(f"Gemini API Quota Exceeded (429). Falling back to rule-based recommendations. Error: {llm_error}")
            else:
                print(f"Gemini LLM Refinement failed. Falling back to rule-based. Error: {llm_error}")
            refined_recs = rule_recs

        # Phase 8: Store context
        session_id = f"ctx_{current_user_id}_{len(ai_context_store)}"
        ai_context_store[session_id] = {
            "room_type": room_type,
            "style": style,
            "description": description,
            "detected_objects": [obj['label'] for obj in detected_objects]
        }

        return jsonify({
            "message": "Room analysis complete",
            "context_id": session_id,
            "room_type": room_type,
            "description": description,
            "detected_objects": [obj['label'] for obj in detected_objects],
            "recommended_items": refined_recs
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error analyzing room: {e}")
        return jsonify({"message": f"Error processing image: {str(e)}"}), 500

@ai_bp.route("/extract-colors", methods=["POST"])
@jwt_required()
def extract_colors():
    if 'image' not in request.files:
        return jsonify({"message": "No image provided"}), 400

    file = request.files['image']
    try:
        # Load image via OpenCV
        in_memory_file = io.BytesIO(file.read())
        file_bytes = np.frombuffer(in_memory_file.getvalue(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize to speed up clustering
        img = cv2.resize(img, (200, 200), interpolation=cv2.INTER_AREA)
        
        # Reshape for clustering
        pixels = img.reshape(-1, 3)
        
        # K-Means clustering
        kmeans = KMeans(n_clusters=5, n_init=10)
        kmeans.fit(pixels)
        
        # Get centers (colors)
        colors = kmeans.cluster_centers_.astype(int)
        
        # Convert to hex
        hex_colors = [
            '#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2])
            for c in colors
        ]
        
        # Basic style recommendation logic
        style = "Modern"
        avg_v = np.mean(colors)
        if avg_v > 180: style = "Minimalist"
        elif avg_v < 80: style = "Industrial"
        
        return jsonify({
            "dominant_color": hex_colors[0],
            "palette": hex_colors,
            "recommended_style": style
        }), 200

    except Exception as e:
        print(f"Error extracting colors: {e}")
        return jsonify({"message": f"Error extracting colors: {str(e)}"}), 500

@ai_bp.route("/analyze-layout", methods=["POST"])
@jwt_required()
def analyze_layout():
    data = request.get_json()
    if not data or 'objects' not in data:
        return jsonify({"message": "No objects data provided"}), 400

    objects = data.get('objects', [])
    if len(objects) < 2:
        return jsonify({
            "clutter_score": 0.0,
            "suggestions": ["Add more items to analyze layout density."]
        }), 200

    try:
        suggestions = []
        clutter_score = 0.0
        
        # Simple density/distance check
        overlaps = 0
        min_distance = 100.0
        
        for i in range(len(objects)):
            obj_a = objects[i]
            pos_a = obj_a.get('position', {'x': 0, 'y': 0, 'z': 0})
            
            for j in range(i + 1, len(objects)):
                obj_b = objects[j]
                pos_b = obj_b.get('position', {'x': 0, 'y': 0, 'z': 0})
                
                # Euclidean distance
                dist = np.sqrt(
                    (pos_a['x'] - pos_b['x'])**2 + 
                    (pos_a['y'] - pos_b['y'])**2 + 
                    (pos_a['z'] - pos_b['z'])**2
                )
                
                if dist < 0.3: # Threshold for "too close" (30cm)
                    overlaps += 1
                
                if dist < min_distance:
                    min_distance = dist
        
        # Normalize clutter score
        clutter_score = min(1.0, (overlaps / len(objects)) + (0.5 if len(objects) > 10 else 0))
        
        if clutter_score > 0.5:
            suggestions.append("The room looks slightly crowded. Consider increasing space between items.")
        if overlaps > 0:
            suggestions.append(f"Detected {overlaps} potential collisions or very close placements.")
        if min_distance > 2.0 and len(objects) > 2:
            suggestions.append("Items are spread quite far apart. Try grouping them for a cozy feel.")
            
        if not suggestions:
            suggestions.append("Layout looks balanced!")

        return jsonify({
            "clutter_score": round(clutter_score, 2),
            "suggestions": suggestions
        }), 200

    except Exception as e:
        print(f"Error analyzing layout: {e}")
        return jsonify({"message": f"Error analyzing layout: {str(e)}"}), 500
