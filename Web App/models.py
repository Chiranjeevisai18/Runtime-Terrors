"""
Database models for Gruha Alankara Web Application.
Defines User, Design, and FurniturePlacement tables using SQLAlchemy ORM.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy instance (attached to Flask app in app.py)
db = SQLAlchemy()


class User(db.Model):
    """
    User model for authentication and design ownership.
    Stores user credentials and links to their saved designs.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship: one user has many designs
    designs = db.relationship('Design', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and store password securely using werkzeug."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Design(db.Model):
    """
    Design model storing uploaded room images and AI analysis results.
    Each design belongs to a user and can have multiple furniture placements.
    """
    __tablename__ = 'designs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_path = db.Column(db.String(256), nullable=False)
    room_type = db.Column(db.String(50), default='unknown')
    style = db.Column(db.String(50), default='modern')
    ai_output = db.Column(db.Text, default='{}')  # JSON string of AI analysis
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship: one design has many furniture placements
    placements = db.relationship('FurniturePlacement', backref='design', lazy=True,
                                  cascade='all, delete-orphan')
    
    @property
    def front_image(self):
        """Extract the front image filename from the JSON image_path or return raw path for legacy data."""
        import json
        try:
            paths = json.loads(self.image_path)
            if isinstance(paths, dict):
                return paths.get('front', '')
            return str(self.image_path)
        except (json.JSONDecodeError, TypeError):
            return self.image_path

    def __repr__(self):
        return f'<Design {self.id} by User {self.user_id}>'


class FurniturePlacement(db.Model):
    """
    Tracks individual furniture items placed in the 3D studio.
    Stores position, rotation, and scale for each piece.
    """
    __tablename__ = 'furniture_placements'
    
    id = db.Column(db.Integer, primary_key=True)
    design_id = db.Column(db.Integer, db.ForeignKey('designs.id'), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)  # e.g., 'sofa', 'table'
    position_x = db.Column(db.Float, default=0.0)
    position_y = db.Column(db.Float, default=0.0)
    position_z = db.Column(db.Float, default=0.0)
    rotation = db.Column(db.Float, default=0.0)  # Y-axis rotation in radians
    scale = db.Column(db.Float, default=1.0)
    color = db.Column(db.String(7), default='#8b5cf6')  # Hex color
    
    def to_dict(self):
        """Convert placement to dictionary for JSON API responses."""
        return {
            'id': self.id,
            'model_name': self.model_name,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'position_z': self.position_z,
            'rotation': self.rotation,
            'scale': self.scale,
            'color': self.color
        }
    
    def __repr__(self):
        return f'<FurniturePlacement {self.model_name} in Design {self.design_id}>'


class FurnitureItem(db.Model):
    """
    Catalog of available furniture items for purchase.
    Stores product details, pricing, and 3D model paths.
    """
    __tablename__ = 'furniture_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # sofa, table, chair, etc.
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    model_path = db.Column(db.String(256))  # Path to GLB/GLTF file
    image_path = db.Column(db.String(256))  # Product image
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'price': self.price,
            'model_path': self.model_path,
            'image_path': self.image_path,
            'stock': self.stock
        }
    
    def __repr__(self):
        return f'<FurnitureItem {self.name}>'


class Order(db.Model):
    """
    Furniture order tracking system.
    Links users to their furniture purchases.
    """
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    design_id = db.Column(db.Integer, db.ForeignKey('designs.id'), nullable=True)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    shipping_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    user = db.relationship('User', backref='orders')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'design_id': self.design_id,
            'total_amount': self.total_amount,
            'status': self.status,
            'shipping_address': self.shipping_address,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }
    
    def __repr__(self):
        return f'<Order {self.id} - {self.status}>'


class OrderItem(db.Model):
    """
    Individual items within an order.
    """
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    furniture_id = db.Column(db.Integer, db.ForeignKey('furniture_items.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)  # Price at time of order
    
    furniture = db.relationship('FurnitureItem', backref='order_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'furniture_id': self.furniture_id,
            'furniture_name': self.furniture.name if self.furniture else 'Unknown',
            'quantity': self.quantity,
            'price': self.price
        }
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'
