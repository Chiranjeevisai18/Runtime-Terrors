"""
API Blueprint for Gruha Alankara.
Provides JSON endpoints for the 3D studio (furniture placements, model list, voice assistant).
"""

import json
from flask import Blueprint, request, jsonify, session
from models import db, Design, FurniturePlacement

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


def api_login_required(f):
    """Decorator to protect API routes - returns JSON error instead of redirect."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    
    return decorated_function


@api_bp.route('/design/<int:design_id>', methods=['GET'])
@api_login_required
def get_design(design_id):
    """
    Get design data including AI output and furniture placements.
    Used by the Three.js studio to initialize the scene.
    """
    design = Design.query.get_or_404(design_id)
    
    if design.user_id != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    ai_output = json.loads(design.ai_output) if design.ai_output else {}
    placements = [p.to_dict() for p in design.placements]
    
    return jsonify({
        'id': design.id,
        'image_path': design.image_path,
        'room_type': design.room_type,
        'style': design.style,
        'ai_output': ai_output,
        'placements': placements
    })


@api_bp.route('/design/<int:design_id>/placements', methods=['POST'])
@api_login_required
def save_placements(design_id):
    """
    Save furniture placements for a design.
    Replaces all existing placements with the new set.
    Used by the Three.js studio when the user clicks 'Save'.
    """
    design = Design.query.get_or_404(design_id)
    
    if design.user_id != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if not data or 'placements' not in data:
        return jsonify({'error': 'No placement data provided'}), 400
    
    # Delete existing placements
    FurniturePlacement.query.filter_by(design_id=design_id).delete()
    
    # Save new placements
    for p in data['placements']:
        placement = FurniturePlacement(
            design_id=design_id,
            model_name=p.get('model_name', 'unknown'),
            position_x=p.get('position_x', 0),
            position_y=p.get('position_y', 0),
            position_z=p.get('position_z', 0),
            rotation=p.get('rotation', 0),
            scale=p.get('scale', 1),
            color=p.get('color', '#8b5cf6')
        )
        db.session.add(placement)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Placements saved successfully',
        'count': len(data['placements'])
    })


@api_bp.route('/models', methods=['GET'])
@api_login_required
def list_models():
    """
    List available 3D furniture models.
    Returns procedural furniture definitions (type, dimensions, color).
    """
    # Procedural furniture definitions (no .glb files needed)
    furniture_models = {
        'sofa': {
            'name': 'Sofa',
            'type': 'sofa',
            'width': 2.0, 'height': 0.8, 'depth': 0.9,
            'color': '#6366f1',
            'description': 'Comfortable three-seater sofa'
        },
        'table': {
            'name': 'Coffee Table',
            'type': 'table',
            'width': 1.2, 'height': 0.45, 'depth': 0.6,
            'color': '#92400e',
            'description': 'Modern coffee table'
        },
        'chair': {
            'name': 'Chair',
            'type': 'chair',
            'width': 0.5, 'height': 0.9, 'depth': 0.5,
            'color': '#7c3aed',
            'description': 'Ergonomic dining chair'
        },
        'bed': {
            'name': 'Bed',
            'type': 'bed',
            'width': 1.8, 'height': 0.5, 'depth': 2.0,
            'color': '#1e40af',
            'description': 'Queen-size bed frame'
        },
        'wardrobe': {
            'name': 'Wardrobe',
            'type': 'wardrobe',
            'width': 1.5, 'height': 2.0, 'depth': 0.6,
            'color': '#78350f',
            'description': 'Two-door wardrobe'
        },
        'bookshelf': {
            'name': 'Bookshelf',
            'type': 'bookshelf',
            'width': 0.8, 'height': 1.8, 'depth': 0.3,
            'color': '#92400e',
            'description': 'Five-tier bookshelf'
        },
        'lamp': {
            'name': 'Floor Lamp',
            'type': 'lamp',
            'width': 0.3, 'height': 1.5, 'depth': 0.3,
            'color': '#f59e0b',
            'description': 'Modern floor lamp'
        },
        'desk': {
            'name': 'Study Desk',
            'type': 'desk',
            'width': 1.2, 'height': 0.75, 'depth': 0.6,
            'color': '#78350f',
            'description': 'Work/study desk'
        },
        'rug': {
            'name': 'Area Rug',
            'type': 'rug',
            'width': 2.5, 'height': 0.02, 'depth': 1.5,
            'color': '#7c3aed',
            'description': 'Decorative area rug'
        },
        'tv_stand': {
            'name': 'TV Stand',
            'type': 'tv_stand',
            'width': 1.5, 'height': 0.5, 'depth': 0.4,
            'color': '#1f2937',
            'description': 'Entertainment center'
        },
        'dining_table': {
            'name': 'Dining Table',
            'type': 'dining_table',
            'width': 1.6, 'height': 0.75, 'depth': 0.9,
            'color': '#92400e',
            'description': 'Six-seater dining table'
        },
        'side_table': {
            'name': 'Side Table',
            'type': 'side_table',
            'width': 0.4, 'height': 0.55, 'depth': 0.4,
            'color': '#78350f',
            'description': 'Bedside/side table'
        },
        'plant': {
            'name': 'Indoor Plant',
            'type': 'plant',
            'width': 0.4, 'height': 1.0, 'depth': 0.4,
            'color': '#059669',
            'description': 'Decorative indoor plant'
        },
        'mirror': {
            'name': 'Wall Mirror',
            'type': 'mirror',
            'width': 0.6, 'height': 1.2, 'depth': 0.05,
            'color': '#94a3b8',
            'description': 'Full-length wall mirror'
        }
    }
    
    return jsonify(furniture_models)


@api_bp.route('/voice-assist', methods=['POST'])
@api_login_required
def voice_assist():
    """
    Voice Assistant Endpoint.
    Accepts a text query about interior design and returns AI-generated advice with TTS audio.
    """
    data = request.get_json()
    query = data.get('query', '') if data else ''
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        from voice_assistant import get_design_advice
        result = get_design_advice(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'text': 'I apologize, the voice assistant is temporarily unavailable. Please try again later.',
            'error': str(e)
        })


@api_bp.route('/product-search', methods=['POST'])
@api_login_required
def product_search():
    """
    Search for real products on Amazon using Tavily search API.
    Accepts a furniture type + style and returns matching product links.
    """
    data = request.get_json()
    query = data.get('query', '') if data else ''
    style = data.get('style', 'modern') if data else 'modern'

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        from flask import current_app
        from tavily import TavilyClient

        api_key = current_app.config.get('TAVILY_API_KEY', '')
        if not api_key:
            return jsonify({'error': 'Tavily API key not configured'}), 500

        client = TavilyClient(api_key=api_key)

        # Build a targeted search query for Amazon furniture
        search_query = f"{query} {style} furniture buy site:amazon.in OR site:amazon.com"

        response = client.search(
            query=search_query,
            search_depth="basic",
            max_results=5,
            include_images=True,
            include_answer=False,
        )

        products = []
        for result in response.get('results', []):
            products.append({
                'title': result.get('title', ''),
                'url': result.get('url', ''),
                'snippet': result.get('content', '')[:200],
                'source': result.get('url', '').split('/')[2] if '/' in result.get('url', '') else '',
            })

        # Attach any images from the response
        images = response.get('images', [])
        for i, product in enumerate(products):
            if i < len(images):
                product['image'] = images[i]
            else:
                product['image'] = ''

        return jsonify({
            'query': query,
            'products': products
        })

    except Exception as e:
        print(f"[API] Tavily search error: {e}")
        return jsonify({
            'error': f'Product search failed: {str(e)}',
            'products': []
        }), 500
