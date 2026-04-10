from sqlalchemy.orm import Session
from app.models.wishlist import Wishlist


def add_to_wishlist(db: Session, user_id: int, product_id: int):
    existing = db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.product_id == product_id
    ).first()

    if existing:
        return existing

    wishlist = Wishlist(user_id=user_id, product_id=product_id)
    db.add(wishlist)
    db.commit()
    db.refresh(wishlist)
    return wishlist

def get_wishlist(db: Session, user_id: int):
    return db.query(Wishlist).filter(Wishlist.user_id == user_id).all()

def remove_from_wishlist(db: Session, wishlist_id: int):
    wishlist = db.query(Wishlist).filter(Wishlist.id == wishlist_id).first()

    if not wishlist:
        return None
    db.delete(wishlist)
    db.commit()
    return wishlist