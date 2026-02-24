"""Quick debug endpoint to check rendered studio HTML output"""
from flask import Flask, render_template_string
import json, os, sys

# Add the project to path
sys.path.insert(0, os.path.dirname(__file__))
from app import create_app

app = create_app()

with app.test_client() as client:
    # Simulate a login
    with app.app_context():
        from models import db, User, Design
        # Get first user and design
        user = db.session.query(User).first()
        design = db.session.query(Design).order_by(Design.id.desc()).first()

        if not user or not design:
            print("No user or design found!")
            sys.exit(1)

        print(f"User: {user.username} (id={user.id})")
        print(f"Design: id={design.id}, image_path={design.image_path[:100]}")
        print(f"Room: {design.room_type}, Style: {design.style}")

        # Parse face_urls the same way as designs.py
        from flask import url_for
        face_urls = {}
        image_path_raw = design.image_path or ''
        try:
            face_paths = json.loads(image_path_raw)
            if isinstance(face_paths, dict):
                for face, filename in face_paths.items():
                    face_urls[face] = url_for('uploaded_file', filename=filename)
            else:
                face_urls['front'] = url_for('uploaded_file', filename=str(face_paths))
        except (json.JSONDecodeError, TypeError):
            if image_path_raw:
                face_urls['front'] = url_for('uploaded_file', filename=image_path_raw)

        print(f"\nface_urls dict: {json.dumps(face_urls, indent=2)}")

        # Now test what the Jinja tojson filter produces
        test_template = """{{ face_urls | tojson }}"""
        result = render_template_string(test_template, face_urls=face_urls)
        print(f"\ntojson output: {result}")

        # Now render the actual studio template and extract the STUDIO_DATA script
        from flask import session as flask_session
        flask_session['user_id'] = user.id
        flask_session['username'] = user.username

        # Build the full context
        ai_result = json.loads(design.ai_output or '{}')
        placements = []

        try:
            rendered = render_template_string(
                """<script>
    window.STUDIO_DATA = {
        designId: {{ design.id }},
        faceUrls: {{ face_urls | tojson }},
        roomType: {{ design.room_type | tojson }},
        style: {{ design.style | tojson }},
        aiOutput: {{ ai_output | tojson }},
        placements: {{ placements | tojson }},
        csrfToken: "test_token"
    };
</script>""",
                design=design,
                face_urls=face_urls,
                ai_output=ai_result,
                placements=placements
            )
            print(f"\nRendered STUDIO_DATA script:\n{rendered}")
        except Exception as e:
            print(f"\nTemplate rendering ERROR: {e}")
