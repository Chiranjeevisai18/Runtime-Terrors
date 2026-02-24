from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.

    Request JSON:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepassword"
        }

    Response JSON (201):
        {
            "message": "User registered successfully",
            "token": "<jwt_token>",
            "user": { "id": "1", "name": "John Doe", "email": "john@example.com" }
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # Validation
    errors = []
    if not name:
        errors.append("Name is required")
    if not email:
        errors.append("Email is required")
    elif "@" not in email:
        errors.append("Invalid email format")
    if not password:
        errors.append("Password is required")
    elif len(password) < 6:
        errors.append("Password must be at least 6 characters")

    if errors:
        return jsonify({"message": "; ".join(errors)}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "An account with this email already exists"}), 409

    # Create user
    user = User(name=name, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Generate JWT token
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "User registered successfully",
        "token": access_token,
        "user": user.to_dict()
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and return JWT token.

    Request JSON:
        {
            "email": "john@example.com",
            "password": "securepassword"
        }

    Response JSON (200):
        {
            "token": "<jwt_token>",
            "user": { "id": "1", "name": "John Doe", "email": "john@example.com" }
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Find user
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password"}), 401

    # Generate JWT token
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": access_token,
        "user": user.to_dict()
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user profile.
    Requires: Authorization: Bearer <token>
    """
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({"user": user.to_dict()}), 200
