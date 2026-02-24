from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os

# Create Blueprint
products_bp = Blueprint("products", __name__, url_prefix="/api/products")

@products_bp.route("/search", methods=["POST"])
@jwt_required()
def search_products():
    """
    Search for products using Playwright Scraper
    """
    data = request.get_json()
    query = data.get("query")
    
    if not query:
        return jsonify({"message": "Search query is required"}), 400
        
    try:
        from services.product_scraper import get_or_scrape_products
        results = get_or_scrape_products(query)
        
        return jsonify({
            "message": "Products retrieved successfully",
            "query": query,
            "results": results
        }), 200
    except Exception as e:
        print(f"Error in product search: {e}")
        return jsonify({"message": "Failed to search products", "error": str(e)}), 500

@products_bp.route("/book", methods=["POST"])
@jwt_required()
def auto_book_product():
    """
    Initiates LangChain Agent to automatically book a product.
    If Agent fails or needs info, returns FALLBACK or INFO_REQUIRED.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    product_url = data.get("product_url")
    
    if not product_url:
        return jsonify({"message": "Product URL is required"}), 400
        
    try:
        # User requested to bypass the LangChain agent security flow and 
        # go straight to the fallback browser link to buy the product.
        return jsonify({
            "status": "FALLBACK",
            "message": "Redirecting to product page for purchase.",
            "redirect_url": product_url
        }), 200
        
    except Exception as e:
        print(f"Error in booking: {e}")
        return jsonify({
            "status": "ERROR",
            "message": "Failed to handle product booking redirection.",
            "redirect_url": product_url
        }), 500

@products_bp.route("/book/resume", methods=["POST"])
@jwt_required()
def resume_booking():
    """
    Resumes an agent session that was paused for user input.
    """
    data = request.get_json()
    session_id = data.get("session_id")
    user_answer = data.get("answer")
    
    if not session_id or not user_answer:
        return jsonify({"message": "Session ID and Answer are required"}), 400
        
    try:
        # TODO: Resume Agent Logic
        return jsonify({
            "status": "FAILED",
            "message": "Resume logic not implemented"
        }), 501
    except Exception as e:
        return jsonify({"message": str(e)}), 500
