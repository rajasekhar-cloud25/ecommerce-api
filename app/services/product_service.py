from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.product import Product
from app.models.review import CustomerReview
from app.services.search_sync import (
    search_products_in_opensearch,
    index_product,
    delete_product_from_index,
)


def create_product(db: Session, data):
    product = Product(
        title=data.title,
        description=data.description,
        price=data.price,
        stock=data.stock,
        brand=data.brand,
        images=data.images,
        is_published=data.is_published,
        category_id=data.category_id,
        discount_percentage=data.discount_percentage,
        is_available=data.is_available,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    index_product(product)
    return product


def get_all_products(db: Session):
    return db.query(Product).all()


def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    db.delete(product)
    db.commit()

    delete_product_from_index(product_id)
    return product


def update_product(db: Session, product_id: int, data):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    index_product(product)
    return product


def search_products(db: Session, search=None, category_id=None, min_price=None, max_price=None, sort=None):

    if search:
        matched_ids = search_products_in_opensearch(search)

        if matched_ids is not None:
            q = db.query(Product).filter(Product.id.in_(matched_ids))

            if category_id:
                q = q.filter(Product.category_id == category_id)
            if min_price is not None:
                q = q.filter(Product.price >= min_price)
            if max_price is not None:
                q = q.filter(Product.price <= max_price)

            results = q.all()
            attach_ratings(db, results)
            return results

    q = db.query(Product)

    if search:
        like = f"%{search}%"
        q = q.filter(or_(
            Product.title.ilike(like),
            Product.brand.ilike(like),
            Product.description.ilike(like),
        ))

    if category_id:
        q = q.filter(Product.category_id == category_id)

    if min_price is not None:
        q = q.filter(Product.price >= min_price)

    if max_price is not None:
        q = q.filter(Product.price <= max_price)

    if sort == "price_asc":
        q = q.order_by(Product.price.asc())
    elif sort == "price_desc":
        q = q.order_by(Product.price.desc())
    elif sort == "newest":
        q = q.order_by(Product.created_at.desc())
    else:
        q = q.order_by(Product.id.asc())

    results = q.all()
    attach_ratings(db, results)
    return results


def attach_ratings(db, products):
    if not products:
        return

    ids = [p.id for p in products]

    rows = db.query(
        CustomerReview.product_id,
        func.avg(CustomerReview.rating).label("avg"),
        func.count(CustomerReview.id).label("count"),
    ).filter(
        CustomerReview.product_id.in_(ids)
    ).group_by(CustomerReview.product_id).all()

    rating_map = {}
    for row in rows:
        rating_map[row.product_id] = (float(row.avg), int(row.count))

    for product in products:
        if product.id in rating_map:
            product.avg_rating, product.review_count = rating_map[product.id]
        else:
            product.avg_rating = 0.0
            product.review_count = 0