from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from app.models.review import CustomerReview
from app.models.order import Order, OrderItem


def create_review(db: Session, user_id: int, data):
    review = CustomerReview(
        user_id=user_id,
        product_id=data.product_id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_product_reviews(db: Session, product_id: int):
    return db.query(CustomerReview).filter(CustomerReview.product_id == product_id).all()


def update_review(db: Session, review_id: int, data):
    review = db.query(CustomerReview).filter(CustomerReview.id == review_id).first()

    if not review:
        return None

    updated_data = data.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review_id: int):
    review = db.query(CustomerReview).filter(CustomerReview.id == review_id).first()

    if not review:
        return None

    db.delete(review)
    db.commit()
    return review


def get_product_rating_summary(db: Session, product_id: int):
    """Return (average_rating, review_count) for a product."""
    result = db.query(
        sql_func.avg(CustomerReview.rating).label("avg"),
        sql_func.count(CustomerReview.id).label("count"),
    ).filter(CustomerReview.product_id == product_id).first()

    avg = float(result.avg) if result.avg else 0.0
    count = int(result.count) if result.count else 0
    return avg, count


def has_user_purchased_product(db: Session, user_id: int, product_id: int):
    """Check if a user has bought this product in a confirmed/shipped/delivered order."""
    order = db.query(Order).join(OrderItem).filter(
        Order.user_id == user_id,
        OrderItem.product_id == product_id,
        Order.status.in_(["confirmed", "shipped", "delivered"]),
        ).first()
    return order is not None


def has_user_reviewed_product(db: Session, user_id: int, product_id: int):
    """Check if a user has already reviewed this product."""
    review = db.query(CustomerReview).filter(
        CustomerReview.user_id == user_id,
        CustomerReview.product_id == product_id,
        ).first()
    return review is not None