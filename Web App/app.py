"""
Gruha Alankara – AI-Powered Interior Design Web Studio
Main Flask Application Entry Point.

This file initializes the Flask app, registers blueprints,
configures the database, and defines core routes.
"""

import os
from flask import Flask, render_template, session, send_from_directory
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from models import db

# ============================================================
# Flask App Factory
# ============================================================

def create_app(test_config=None):
    """
    Create and configure the Flask application.
    Uses the app factory pattern for modularity and testability.

    Args:
        test_config: Optional dict of config overrides (used in testing).
                     Pass e.g. {'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'}
                     to use an isolated in-memory database during tests.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Apply test config overrides BEFORE initialising extensions
    if test_config:
        app.config.update(test_config)

    # ---- Initialize Extensions ----

    # Database ORM
    db.init_app(app)

    # CSRF Protection for all forms
    csrf = CSRFProtect(app)

    # Rate Limiting (protects upload endpoint from abuse)
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[Config.RATELIMIT_DEFAULT]
    )

    # ---- Register Blueprints ----
    from blueprints.auth import auth_bp
    from blueprints.designs import designs_bp
    from blueprints.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(designs_bp)
    app.register_blueprint(api_bp)

    # Exempt API routes from CSRF (they use JSON, not forms)
    csrf.exempt(api_bp)

    # Apply rate limiting to upload endpoint
    limiter.limit(Config.RATELIMIT_UPLOAD)(designs_bp)

    # ---- Create Database Tables ----
    with app.app_context():
        db.create_all()
        print("[App] Database tables created/verified.")

    # ---- Ensure Directories Exist ----
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'audio'), exist_ok=True)

    # ---- Core Routes ----

    @app.route('/')
    def home():
        """Landing page route."""
        return render_template('index.html')

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        """Serve uploaded images."""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # ---- Context Processors ----

    @app.context_processor
    def inject_user():
        """Make user info available in all templates."""
        return {
            'logged_in': 'user_id' in session,
            'current_username': session.get('username', '')
        }

    # ---- Error Handlers ----

    @app.errorhandler(404)
    def not_found(e):
        return render_template('base.html', error_message="Page not found"), 404

    @app.errorhandler(413)
    def too_large(e):
        return render_template('base.html', error_message="File too large. Maximum size is 16MB."), 413

    @app.errorhandler(500)
    def server_error(e):
        return render_template('base.html', error_message="Internal server error"), 500

    return app


# ============================================================
# Application Entry Point
# ============================================================

if __name__ == '__main__':
    app = create_app()
    print("\n" + "=" * 60)
    print("  Gruha Alankara - AI Interior Design Studio")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000)
