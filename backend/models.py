from datetime import datetime
from extensions import db, bcrypt


class User(db.Model):
    """User model for authentication."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    designs = db.relationship("Design", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str):
        """Hash and set the user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """Serialize user to dictionary (safe — no password)."""
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
        }

    def __repr__(self):
        return f"<User {self.email}>"


class Design(db.Model):
    """Saved AR design metadata (for V2)."""
    __tablename__ = "designs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    anchors_json = db.Column(db.Text, default="[]")  # Keeping for backward compatibility or simple storage
    snapshot_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to granular objects
    objects = db.relationship("DesignObject", backref="design", lazy=True, cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": str(self.user_id),
            "name": self.name,
            "description": self.description,
            "anchors_json": self.anchors_json,
            "snapshot_path": self.snapshot_path,
            "objects": [obj.to_dict() for obj in self.objects],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Design {self.name}>"


class DesignObject(db.Model):
    """Granular AR object within a design."""
    __tablename__ = "design_objects"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    design_id = db.Column(db.Integer, db.ForeignKey("designs.id"), nullable=False)
    model_id = db.Column(db.String(100), nullable=False)
    
    # Position
    pos_x = db.Column(db.Float, default=0.0)
    pos_y = db.Column(db.Float, default=0.0)
    pos_z = db.Column(db.Float, default=0.0)
    
    # Transform
    rotation = db.Column(db.Float, default=0.0)
    scale = db.Column(db.Float, default=1.0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "model_id": self.model_id,
            "position": {"x": self.pos_x, "y": self.pos_y, "z": self.pos_z},
            "rotation": self.rotation,
            "scale": self.scale
        }

    def __repr__(self):
        return f"<DesignObject {self.model_id} in Design {self.design_id}>"


class Product(db.Model):
    """Real-world products scraped from vendors."""
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(500), nullable=False)
    vendor = db.Column(db.String(100), nullable=False)  # e.g., 'amazon'
    url = db.Column(db.Text, nullable=False)
    price = db.Column(db.String(50), nullable=True)
    rating = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    last_scraped_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "vendor": self.vendor,
            "url": self.url,
            "price": self.price,
            "rating": self.rating,
            "image_url": self.image_url,
            "last_scraped_at": self.last_scraped_at.isoformat() if self.last_scraped_at else None,
        }

    def __repr__(self):
        return f"<Product {self.title[:20]}... from {self.vendor}>"


class Booking(db.Model):
    """Tracks automated agent booking attempts."""
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    
    # SUCCESS, FAILED, INFO_REQUIRED, PROCESSING
    status = db.Column(db.String(50), nullable=False, default="PROCESSING")
    order_id = db.Column(db.String(100), nullable=True)  # Populated on SUCCESS
    failure_reason = db.Column(db.Text, nullable=True)   # Populated on FAILED
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref="bookings", lazy=True)
    product = db.relationship("Product", backref="bookings", lazy=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product": self.product.to_dict() if self.product else None,
            "status": self.status,
            "order_id": self.order_id,
            "failure_reason": self.failure_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Booking {self.id} User {self.user_id} Status {self.status}>"
