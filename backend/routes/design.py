from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Design, DesignObject

design_bp = Blueprint("design", __name__, url_prefix="/api/designs")

@design_bp.route("", methods=["POST"])
@jwt_required()
def save_design():
    """Save a new AR design layout."""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    name = data.get("name", "My Design").strip()
    objects_data = data.get("objects", [])

    try:
        # Create the design
        design = Design(
            user_id=int(user_id),
            name=name,
            description=data.get("description", ""),
            anchors_json=str(objects_data) # Simplified backup
        )
        db.session.add(design)
        db.session.flush() # Get the design ID

        # Create objects
        for obj in objects_data:
            pos = obj.get("position", {"x": 0, "y": 0, "z": 0})
            new_obj = DesignObject(
                design_id=design.id,
                model_id=obj.get("model_id"),
                pos_x=pos.get("x", 0.0),
                pos_y=pos.get("y", 0.0),
                pos_z=pos.get("z", 0.0),
                rotation=obj.get("rotation", 0.0),
                scale=obj.get("scale", 1.0)
            )
            db.session.add(new_obj)

        db.session.commit()
        return jsonify(design.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error saving design: {e}")
        return jsonify({"message": f"Error saving design: {str(e)}"}), 500

@design_bp.route("", methods=["GET"])
@jwt_required()
def get_designs():
    """Fetch all designs for the current user."""
    user_id = get_jwt_identity()
    designs = Design.query.filter_by(user_id=int(user_id)).order_by(Design.created_at.desc()).all()
    
    return jsonify([d.to_dict() for d in designs]), 200

@design_bp.route("/<int:design_id>", methods=["GET"])
@jwt_required()
def get_design_detail(design_id):
    """Fetch details for a specific design."""
    user_id = get_jwt_identity()
    design = Design.query.filter_by(id=design_id, user_id=int(user_id)).first()

    if not design:
        return jsonify({"message": "Design not found"}), 404

    return jsonify(design.to_dict()), 200

@design_bp.route("/<int:design_id>", methods=["DELETE"])
@jwt_required()
def delete_design(design_id):
    """Delete a design."""
    user_id = get_jwt_identity()
    design = Design.query.filter_by(id=design_id, user_id=int(user_id)).first()

    if not design:
        return jsonify({"message": "Design not found"}), 404

    try:
        db.session.delete(design)
        db.session.commit()
        return jsonify({"message": "Design deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting design: {str(e)}"}), 500
