from sqlalchemy.orm import Session
from app.models.cart import Cart, CartItem

def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int):
    cart_exists = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart_exists:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    else:
        cart = cart_exists

    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id, CartItem.product_id == product_id
    ).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id, product_id=product_id, quantity=quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item


def get_all_cart_items(db: Session, user_id: int):
    return db.query(Cart).filter(Cart.user_id == user_id).first()

def remove_cart_item(db: Session, cart_item_id: int):
    cart_item_by_id = db.query(CartItem).filter(CartItem.id == cart_item_id).first()

    if cart_item_by_id:
        db.delete(cart_item_by_id)
        db.commit()
    return cart_item_by_id


def update_cart_quantity(db: Session, cart_item_id: int, quantity: int):
    cart_by_id = db.query(CartItem).filter(CartItem.id == cart_item_id).first()

    if not cart_by_id:
        return None

    cart_by_id.quantity += quantity
    db.commit()
    db.refresh(cart_by_id)
    return cart_by_id


