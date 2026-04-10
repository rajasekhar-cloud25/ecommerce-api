"""
Seed module — populates categories + products from DummyJSON.
Called automatically on FastAPI startup.
"""
import requests
from sqlalchemy.orm import Session
from app.models.category import Category
from app.models.product import Product


CATEGORY_MAP = {
    # Electronics
    "smartphones": "Electronics",
    "laptops": "Electronics",
    "tablets": "Electronics",
    "mobile-accessories": "Electronics",

    # Men's fashion
    "mens-shirts": "Men's Clothing",
    "mens-shoes": "Men's Clothing",
    "mens-watches": "Men's Clothing",

    # Women's fashion
    "womens-dresses": "Women's Clothing",
    "womens-shoes": "Women's Clothing",
    "womens-bags": "Women's Clothing",
    "womens-jewellery": "Women's Clothing",
    "womens-watches": "Women's Clothing",
    "tops": "Women's Clothing",

    # Beauty
    "fragrances": "Beauty",
    "skincare": "Beauty",
    "beauty": "Beauty",

    # Home
    "home-decoration": "Home",
    "furniture": "Home",
    "lighting": "Home",
    "kitchen-accessories": "Home",

    # Accessories
    "sunglasses": "Accessories",

    # Groceries
    "groceries": "Groceries",

    # Sports
    "sports-accessories": "Sports",

    # Auto
    "automotive": "Automotive",
    "motorcycle": "Automotive",
    "vehicle": "Automotive",
}


def seed_database(db: Session):
    # Skip if already seeded
    existing_count = db.query(Product).count()
    if existing_count > 5:
        print(f"⏭️  Seed skipped — {existing_count} products already in DB")
        return

    print("🌱 Seeding database from DummyJSON...")

    try:
        response = requests.get("https://dummyjson.com/products?limit=100", timeout=10)
        response.raise_for_status()
        products = response.json().get("products", [])
    except Exception as e:
        print(f"⚠️  Could not fetch seed data: {e}")
        return

    # Create categories
    category_cache = {}
    for friendly_name in set(CATEGORY_MAP.values()):
        existing = db.query(Category).filter(Category.name == friendly_name).first()
        if existing:
            category_cache[friendly_name] = existing
        else:
            cat = Category(name=friendly_name, description=f"{friendly_name} products")
            db.add(cat)
            db.flush()
            category_cache[friendly_name] = cat
    db.commit()

    # Insert products
    inserted = 0
    for p in products:
        friendly = CATEGORY_MAP.get(p.get("category", ""))
        if not friendly:
            continue

        if db.query(Product).filter(Product.title == p["title"]).first():
            continue

        image_url = p.get("thumbnail") or (p.get("images") or [""])[0]

        product = Product(
            title=p["title"],
            description=p.get("description", ""),
            price=float(p.get("price", 0)),
            discount_percentage=float(p.get("discountPercentage", 0)),
            is_available=True,
            is_published=True,
            stock=int(p.get("stock", 0)),
            brand=p.get("brand", "Generic"),
            images=image_url,
            category_id=category_cache[friendly].id,
        )
        db.add(product)
        inserted += 1

    db.commit()
    print(f"✅ Seeded {inserted} products")