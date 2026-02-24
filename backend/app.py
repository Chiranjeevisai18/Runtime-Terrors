import os
from flask import Flask, jsonify
from config import config_by_name
from extensions import db, bcrypt, jwt, cors


def create_app(config_name: str = None) -> Flask:
    """Application factory for Flask app."""

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": "*",  # Allow all origins for development
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    # Register blueprints
    from routes.auth import auth_bp
    from routes.ai import ai_bp
    from routes.design import design_bp
    from routes.assistant import assistant_bp
    from routes.products import products_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(design_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(products_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"message": "Authorization token is required"}), 401

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "app": "Gruha Alankara Backend",
            "version": "1.0.0"
        }), 200

    # Root endpoint
    @app.route("/", methods=["GET"])
    def root():
        return jsonify({
            "app": "Gruha Alankara Backend",
            "version": "1.0.0",
            "endpoints": {
                "health": "/api/health",
                "register": "/api/auth/register",
                "login": "/api/auth/login",
                "profile": "/api/auth/me"
            }
        }), 200

    return app
