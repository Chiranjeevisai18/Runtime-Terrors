from app import create_app
from models import db, FurnitureItem

def seed_furniture():
    app = create_app()
    with app.app_context():
        # Clear existing items to re-seed with images
        FurnitureItem.query.delete()
        
        items = [
            # Sofas
            FurnitureItem(
                name="Velvet Cloud Sofa",
                category="sofa",
                price=899.99,
                description="Deep-seated velvet sofa for ultimate comfort.",
                image_path="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&h=400&fit=crop&q=80"
            ),
            FurnitureItem(
                name="Modern Sectional",
                category="sofa",
                price=1200.00,
                description="Modular sectional sofa with clean lines.",
                image_path="https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=600&h=400&fit=crop&q=80"
            ),
            
            # Chairs
            FurnitureItem(
                name="Eames-Style Lounge",
                category="chair",
                price=450.00,
                description="Classic mid-century modern lounge chair.",
                image_path="https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=600&h=400&fit=crop&q=80"
            ),
            FurnitureItem(
                name="Minimalist Dining Chair",
                category="chair",
                price=120.00,
                description="Sleek wooden chair with a natural finish.",
                image_path="https://images.unsplash.com/photo-1503602642458-232111445657?w=600&h=400&fit=crop&q=80"
            ),
            
            # Tables
            FurnitureItem(
                name="Marble Coffee Table",
                category="table",
                price=350.00,
                description="Elegant marble top table with brass legs.",
                image_path="https://images.unsplash.com/photo-1533090481720-856c6e3c1fdc?w=600&h=400&fit=crop&q=80"
            ),
            FurnitureItem(
                name="Solid Oak Desk",
                category="table",
                price=550.00,
                description="Spacious and durable desk for your home office.",
                image_path="https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600&h=400&fit=crop&q=80"
            ),
            
            # Beds
            FurnitureItem(
                name="Upholstered King Bed",
                category="bed",
                price=1100.00,
                description="Luxurious upholstered bed frame in charcoal gray.",
                image_path="https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=600&h=400&fit=crop&q=80"
            ),
            
            # Storage
            FurnitureItem(
                name="Mid-Century Sideboard",
                category="storage",
                price=650.00,
                description="Stylish storage solution with tapered legs.",
                image_path="https://images.unsplash.com/photo-1595428774223-ef52624120d2?w=600&h=400&fit=crop&q=80"
            ),
        ]
        
        db.session.add_all(items)
        db.session.commit()
        print("Successfully seeded 8 furniture items with images!")

if __name__ == "__main__":
    seed_furniture()
