"""
Recommendation Engine for Gruha Alankara.
Provides rule-based furniture and style recommendations based on
detected objects, room type, and selected design style.
"""

# ============================================================
# Style Theme Definitions
# Each theme specifies furniture preferences, colors, and materials
# ============================================================
STYLE_THEMES = {
    'modern': {
        'name': 'Modern',
        'description': 'Clean lines, high contrast, and a vibrant minimalist glow',
        'color_scheme': ['#0f172a', '#1e293b', '#7c3aed', '#06b6d4', '#f59e0b'],
        'materials': ['Polished Steel', 'Smoked Glass', 'Matte Composite', 'Velvet'],
        'furniture_modifiers': {
            'sofa': {'color': '#7c3aed', 'style': 'Low-profile velvet sectional'},
            'table': {'color': '#06b6d4', 'style': 'Neon-accented glass table'},
            'lamp': {'color': '#f59e0b', 'style': 'Minimalist arc lamp'},
            'chair': {'color': '#334155', 'style': 'Architectural accent chair'},
        }
    },
    'minimalist': {
        'name': 'Minimalist',
        'description': 'Monochromatic serenity with natural organic textures',
        'color_scheme': ['#f8fafc', '#f1f5f9', '#cbd5e1', '#64748b', '#94a3b8'],
        'materials': ['Light Birch', 'Stone Wash Linen', 'Frosted Glass', 'Wool'],
        'furniture_modifiers': {
            'sofa': {'color': '#cbd5e1', 'style': 'Seamless linen sofa'},
            'table': {'color': '#f1f5f9', 'style': 'Simple stone coffee table'},
            'lamp': {'color': '#ffffff', 'style': 'Soft-glow globe light'},
            'chair': {'color': '#94a3b8', 'style': 'Molded shell chair'},
        }
    },
    'traditional': {
        'name': 'Traditional',
        'description': 'Legacy elegance with deep oaks and crimson accents',
        'color_scheme': ['#451a03', '#78350f', '#991b1b', '#b91c1c', '#fef2f2'],
        'materials': ['Walnut', 'Brass', 'Deep Velvet', 'Persian Wool'],
        'furniture_modifiers': {
            'sofa': {'color': '#991b1b', 'style': 'Classic Chesterfield'},
            'table': {'color': '#451a03', 'style': 'Queen Anne tea table'},
            'lamp': {'color': '#b45309', 'style': 'Brass floor candelabra'},
            'chair': {'color': '#78350f', 'style': 'Carved mahogany chair'},
        }
    },
    'industrial': {
        'name': 'Industrial',
        'description': 'Raw structural elements with charcoal and rust tones',
        'color_scheme': ['#171717', '#262626', '#404040', '#737373', '#ea580c'],
        'materials': ['Raw Iron', 'Reclaimed Pine', 'Exposed Concrete', 'Leather'],
        'furniture_modifiers': {
            'sofa': {'color': '#525252', 'style': 'Distressed leather sofa'},
            'table': {'color': '#404040', 'style': 'Metal-frame wood table'},
            'lamp': {'color': '#fb923c', 'style': 'Factory-style pipe lamp'},
            'chair': {'color': '#171717', 'style': 'Steel frame chair'},
        }
    },
    'scandinavian': {
        'name': 'Scandinavian',
        'description': 'Lagom balance with soft pastels and light ash woods',
        'color_scheme': ['#fdfcfb', '#e2e8f0', '#94a3b8', '#38bdf8', '#fb7185'],
        'materials': ['Ash Wood', 'Organic Cotton', 'Ceramic', 'Felt'],
        'furniture_modifiers': {
            'sofa': {'color': '#e2e8f0', 'style': 'Sky-blue felt sofa'},
            'table': {'color': '#fdfcfb', 'style': 'White ash tray table'},
            'lamp': {'color': '#38bdf8', 'style': 'Modern tripod floor lamp'},
            'chair': {'color': '#fb7185', 'style': 'Wishbone chair in coral'},
        }
    }
}

# ============================================================
# Room-Based Furniture Rules
# Defines what furniture to recommend based on room type
# ============================================================
ROOM_FURNITURE_RULES = {
    'bedroom': {
        'essential': ['bed', 'wardrobe', 'side_table'],
        'recommended': ['lamp', 'mirror', 'rug', 'plant'],
        'optional': ['desk', 'chair', 'bookshelf']
    },
    'living_room': {
        'essential': ['sofa', 'table', 'tv_stand'],
        'recommended': ['rug', 'lamp', 'plant', 'bookshelf'],
        'optional': ['chair', 'side_table', 'mirror']
    },
    'kitchen': {
        'essential': ['dining_table', 'chair'],
        'recommended': ['lamp', 'plant'],
        'optional': ['bookshelf', 'side_table']
    },
    'dining_room': {
        'essential': ['dining_table', 'chair'],
        'recommended': ['lamp', 'rug', 'plant', 'mirror'],
        'optional': ['side_table', 'bookshelf']
    },
    'office': {
        'essential': ['desk', 'chair', 'bookshelf'],
        'recommended': ['lamp', 'plant'],
        'optional': ['rug', 'side_table', 'mirror']
    },
    'bathroom': {
        'essential': ['mirror'],
        'recommended': ['plant', 'lamp'],
        'optional': ['side_table']
    }
}

# ============================================================
# Object-Based Additional Rules
# If certain objects are detected, suggest complementary items
# ============================================================
OBJECT_COMPLEMENT_RULES = {
    'bed': ['wardrobe', 'side_table', 'lamp', 'rug'],
    'sofa': ['table', 'rug', 'lamp', 'plant'],
    'couch': ['table', 'rug', 'lamp', 'plant'],
    'chair': ['desk', 'lamp', 'bookshelf'],
    'dining table': ['chair', 'lamp', 'rug'],
    'tv': ['tv_stand', 'sofa', 'rug'],
    'desk': ['chair', 'lamp', 'bookshelf'],
    'potted plant': ['side_table', 'lamp'],
}


# ============================================================
# Default Placement Advice Fallbacks
# Used when high-level AI analysis is unavailable or cached
# ============================================================
PLACEMENT_ADVICE_FALLBACKS = {
    'sofa': {
        'where': 'Against the main wall, facing the entrance',
        'color_logic': 'Deep neutral tones anchored with accent pillows for contrast.',
        'why': 'Maximizes floor space and creates an inviting focal point.',
        'description': 'Contemporary low-profile sectional with soft upholstery.'
    },
    'bed': {
        'where': 'Centered against the North wall',
        'color_logic': 'Soothing cool tones to promote a healthy sleep environment.',
        'why': 'The bed is the primary focal point; North placement aligns with flow.',
        'description': 'Upholstered platform bed with a minimal designer headboard.'
    },
    'table': {
        'where': 'In front of the seating area',
        'color_logic': 'Natural wood finish to add warmth to the modern textures.',
        'why': 'Provides functional utility while grouping the seating arrangement.',
        'description': 'Solid wood coffee table with a matte protective finish.'
    },
    'desk': {
        'where': 'Near the window for natural light',
        'color_logic': 'Concentrated darker tones to minimize visual distractions.',
        'why': 'Spatial separation from the rest of the room aids productivity.',
        'description': 'Ergonomic study desk with integrated cable management.'
    },
    'dining_table': {
        'where': 'Centered in the dining area',
        'color_logic': 'Warm earthy tones to stimulate conversation and appetite.',
        'why': 'Allows for 360-degree movement and equal seating accessibility.',
        'description': 'Tapered-leg dining table with a durable hardwood top.'
    },
    'lamp': {
        'where': 'In the corner or beside seating/bed',
        'color_logic': 'Metallic accents to reflect and diffuse warm light.',
        'why': 'Layered lighting adds depth and coziness to the evening ambiance.',
        'description': 'Minimalist floor lamp with an adjustable arc or globe shade.'
    },
    'rug': {
        'where': 'Centered under the main furniture group',
        'color_logic': 'Geometric patterns to tie together the room\'s color palette.',
        'why': 'Defines the zone and improves acoustic comfort in the space.',
        'description': 'High-density pile rug with a slip-resistant backing.'
    }
}


def get_recommendations(room_type, detected_objects, style='modern'):
    """
    Generate furniture and style recommendations based on:
    - Room type (user-selected or AI-detected)
    - Detected objects in the room image
    - Selected design style

    Args:
        room_type: Type of room (bedroom, living_room, etc.)
        detected_objects: List of objects detected by AI
        style: Design style preference

    Returns:
        Dictionary with recommended furniture, colors, and materials
    """
    # Get style theme (default to modern if not found)
    theme = STYLE_THEMES.get(style, STYLE_THEMES['modern'])

    # Get room-based furniture rules
    room_rules = ROOM_FURNITURE_RULES.get(room_type, ROOM_FURNITURE_RULES['living_room'])

    # Build recommendation list: essential first, then recommended
    recommended = list(room_rules['essential'])
    recommended.extend(room_rules['recommended'])

    # Add complementary furniture based on detected objects
    for obj in detected_objects:
        obj_lower = obj.lower()
        if obj_lower in OBJECT_COMPLEMENT_RULES:
            for complement in OBJECT_COMPLEMENT_RULES[obj_lower]:
                if complement not in recommended:
                    recommended.append(complement)

    # Only skip items that are EXACTLY and CLEARLY already in the room
    detected_lower = [obj.lower() for obj in detected_objects]
    essential_set = set(room_rules['essential'])

    final_furniture = []
    for item in recommended:
        item_key = item.replace('_', ' ')
        already_detected = any(
            item_key == det or item == det.replace(' ', '_')
            for det in detected_lower
        )
        if already_detected and item not in essential_set:
            continue
        final_furniture.append(item)

    # Deduplicate while preserving order
    seen = set()
    unique_furniture = []
    for item in final_furniture:
        if item not in seen:
            seen.add(item)
            unique_furniture.append(item)

    # Always return at least some recommendations
    if not unique_furniture:
        unique_furniture = list(room_rules['essential']) + list(room_rules['recommended'])[:3]

    # Build detailed placement advice for each item
    placement_advice = []
    for item in unique_furniture:
        fallback = PLACEMENT_ADVICE_FALLBACKS.get(item, {
            'where': 'Optimal position based on room flow',
            'color_logic': 'Harmonious color chosen to match the design palette.',
            'why': 'Enhances the overall functionality and balance of the room.',
            'description': f'A stylish {item.replace("_", " ")} that fits your {style} theme.'
        })
        
        # Get item hex from theme if possible, else default
        item_color = theme['furniture_modifiers'].get(item, {}).get('color', theme['color_scheme'][3])
        
        advice = {
            'item': item.replace('_', ' ').title(),
            'where': fallback['where'],
            'color': item_color,
            'color_logic': fallback['color_logic'],
            'why': fallback['why'],
            'description': fallback['description']
        }
        placement_advice.append(advice)

    return {
        'furniture': unique_furniture,
        'style': theme['name'],
        'style_description': theme['description'],
        'color_scheme': theme['color_scheme'],
        'materials': theme['materials'],
        'placement_advice': placement_advice,
        'furniture_details': {
            item: theme['furniture_modifiers'].get(item, {})
            for item in unique_furniture
            if item in theme.get('furniture_modifiers', {})
        }
    }
