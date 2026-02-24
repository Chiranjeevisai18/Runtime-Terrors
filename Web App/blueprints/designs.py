"""
Designs Blueprint for Gruha Alankara.
Handles image upload, AI analysis, dashboard listing, and design management.
"""

import os
import json
import uuid
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, current_app)
from werkzeug.utils import secure_filename
from models import db, Design, FurniturePlacement

# Create designs blueprint
designs_bp = Blueprint('designs', __name__)


def login_required(f):
    """
    Decorator to protect routes that require authentication.
    Redirects unauthenticated users to the login page.
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    
    return decorated_function


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@designs_bp.route('/dashboard')
@login_required
def dashboard():
    """
    User Dashboard Route.
    Displays all saved designs for the logged-in user.
    """
    user_id = session['user_id']
    designs = Design.query.filter_by(user_id=user_id).order_by(Design.created_at.desc()).all()
    return render_template('dashboard.html', designs=designs)


@designs_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    Image Upload Route.
    GET: Display upload form with 6 face image slots.
    POST: Save up to 6 face images, run AI on front face, create design record.
    """
    if request.method == 'POST':
        # ---- Collect face image files ----
        FACE_KEYS = ['face_front', 'face_back', 'face_left', 'face_right', 'face_ceiling', 'face_floor']

        # Front wall is required
        front_file = request.files.get('face_front')
        if not front_file or front_file.filename == '':
            flash('Front wall image is required.', 'error')
            return redirect(request.url)

        if not allowed_file(front_file.filename):
            flash('Invalid file type. Please upload JPG or PNG images.', 'error')
            return redirect(request.url)

        # ---- Get user selections ----
        room_type = request.form.get('room_type', 'living_room')
        style = request.form.get('style', 'modern')

        # ---- Ensure upload directory exists ----
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

        # ---- Save each face image ----
        face_paths = {}   # e.g. {'front': 'abc123_front.jpg', 'back': 'def456_back.jpg'}
        primary_filepath = None  # Path to front image for AI

        for face_key in FACE_KEYS:
            face_name = face_key.replace('face_', '')  # 'front', 'back', etc.
            file = request.files.get(face_key)
            if not file or file.filename == '':
                continue  # Optional face not provided; skip

            if not allowed_file(file.filename):
                continue  # Skip invalid file types silently for optional faces

            ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}_{face_name}.{ext}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)

            # ---- Validate image using Pillow ----
            try:
                from PIL import Image as PILImage
                img = PILImage.open(filepath)
                img.verify()
                face_paths[face_name] = unique_filename
                if face_name == 'front':
                    primary_filepath = filepath
            except Exception:
                os.remove(filepath)
                if face_name == 'front':
                    flash('Front wall image is invalid or corrupted.', 'error')
                    return redirect(request.url)

        if not face_paths.get('front'):
            flash('Front wall image could not be saved.', 'error')
            return redirect(request.url)

        # ---- Run AI Analysis on all uploaded faces ----
        try:
            # Collect all full filepaths for AI
            ai_input_paths = []
            for face_name in FACE_KEYS:
                fname = face_paths.get(face_name.replace('face_', ''))
                if fname:
                    ai_input_paths.append(os.path.join(current_app.config['UPLOAD_FOLDER'], fname))
            
            from ai_engine import analyze_room
            ai_result = analyze_room(ai_input_paths, room_type, style)
        except Exception as e:
            print(f"[Designs] AI room analysis error: {e}")
            ai_result = {
                'room_type': room_type,
                'detected_objects': [],
                'caption': 'AI analysis unavailable.',
                'suggested_style': style,
                'recommended_furniture': ['sofa', 'table', 'lamp', 'bookshelf'],
                'color_scheme': ['#8b5cf6', '#06b6d4', '#f59e0b'],
                'error': str(e)
            }

        # ---- Get furniture recommendations (extended logic) ----
        try:
            from recommender import get_recommendations
            recommendations = get_recommendations(
                room_type,
                ai_result.get('detected_objects', []),
                style
            )
            # Merge recommendations if not already in ai_result
            if not ai_result.get('recommended_furniture'):
                ai_result['recommended_furniture'] = recommendations['furniture']
            if not ai_result.get('color_scheme'):
                ai_result['color_scheme'] = recommendations.get('color_scheme', [])
            ai_result['materials'] = recommendations.get('materials', [])
            
            # Ensure detailed placements always exist (fallback to rule-based if AI missed them)
            if not ai_result.get('detailed_placements'):
                ai_result['detailed_placements'] = recommendations.get('placement_advice', [])
        except Exception as e:
            print(f"[Designs] Recommender error: {e}")
            pass

        # ---- Store face paths as JSON in image_path ----
        # Format: JSON string {"front": "abc.jpg", "back": "def.jpg", ...}
        image_path_value = json.dumps(face_paths)

        # ---- Save design to database ----
        design = Design(
            user_id=session['user_id'],
            image_path=image_path_value,
            room_type=room_type,
            style=style,
            ai_output=json.dumps(ai_result)
        )

        db.session.add(design)
        db.session.commit()

        face_count = len(face_paths)
        flash(f'Room analyzed successfully! {face_count} face image(s) loaded. Open the 3D Studio to start designing.', 'success')
        return redirect(url_for('designs.studio', design_id=design.id))

    return render_template('upload.html')


@designs_bp.route('/studio/<int:design_id>')
@login_required
def studio(design_id):
    """
    3D Visualization Studio Route.
    Loads design data and renders the Three.js interactive scene.
    """
    from flask import url_for as _url_for
    design = Design.query.get_or_404(design_id)

    # Ensure user owns this design
    if design.user_id != session['user_id']:
        flash('You do not have access to this design.', 'error')
        return redirect(url_for('designs.dashboard'))

    # Parse AI output
    ai_output = json.loads(design.ai_output) if design.ai_output else {}

    # Get existing placements
    placements = [p.to_dict() for p in design.placements]

    # Parse face image paths (new format: JSON dict, or legacy: plain filename)
    face_urls = {}  # e.g. {'front': '/uploads/abc.jpg', 'back': '/uploads/def.jpg'}
    image_path_raw = design.image_path or ''
    try:
        # New format: JSON dict
        face_paths = json.loads(image_path_raw)
        if isinstance(face_paths, dict):
            for face, filename in face_paths.items():
                face_urls[face] = _url_for('uploaded_file', filename=filename)
        else:
            # json was a plain string somehow
            face_urls['front'] = _url_for('uploaded_file', filename=str(face_paths))
    except (json.JSONDecodeError, TypeError):
        # Legacy format: single filename string
        if image_path_raw:
            face_urls['front'] = _url_for('uploaded_file', filename=image_path_raw)

    return render_template('studio.html',
                           design=design,
                           ai_output=ai_output,
                           placements=placements,
                           face_urls=face_urls)


@designs_bp.route('/designs/<int:design_id>/delete', methods=['POST'])
@login_required
def delete_design(design_id):
    """
    Delete a design and its associated image file.
    """
    design = Design.query.get_or_404(design_id)
    
    # Ensure user owns this design
    if design.user_id != session['user_id']:
        flash('You do not have access to this design.', 'error')
        return redirect(url_for('designs.dashboard'))
    
    # Delete image file(s) — handles both JSON dict and legacy single filename
    try:
        face_paths = json.loads(design.image_path)
        if isinstance(face_paths, dict):
            for filename in face_paths.values():
                fp = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(fp):
                    os.remove(fp)
        else:
            fp = os.path.join(current_app.config['UPLOAD_FOLDER'], str(face_paths))
            if os.path.exists(fp):
                os.remove(fp)
    except (json.JSONDecodeError, TypeError):
        fp = os.path.join(current_app.config['UPLOAD_FOLDER'], design.image_path)
        if os.path.exists(fp):
            os.remove(fp)
    
    # Delete design record (cascades to placements)
    db.session.delete(design)
    db.session.commit()
    
    flash('Design deleted successfully.', 'info')
    return redirect(url_for('designs.dashboard'))
