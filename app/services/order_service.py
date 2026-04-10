from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.cart import Cart, CartItem
import random
import string
from datetime import datetime

def create_order(db: Session, user_id: int, data):
    order = Order(
        user_id=user_id,
        address_id = data.address_id,
        status = "pending",
        total_price = 0
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    total = 0

    for item in data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        order_item = OrderItem(
            order_id = order.id,
            product_id = item.product_id,
            quantity = item.quantity,
            price = product.price
        )
        db.add(order_item)

        total += product.price * item.quantity

    order.total_price = total
    db.commit()
    db.refresh(order)
    return order

def get_user_orders(db: Session, user_id: int):
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    return orders

def get_order_by_id(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        return None

    return order

def update_order_status(db: Session, order_id: int, status: str):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        return None

    order.status = status
    db.commit()
    db.refresh(order)
    return order


def cancel_order(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        return None

    # can only cancel before shipping
    if order.status in ["shipped", "delivered", "cancelled"]:
        return False

    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    return order


from app.models.cart import Cart, CartItem


def checkout_cart(db: Session, user_id: int, address_id: int = None):
    """Convert user's cart into an order, then clear the cart."""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart or not cart.cart_items:
        return None

    # Create order
    order = Order(
        user_id=user_id,
        address_id=address_id,
        order_number=generate_order_number(),
        status="pending",
        total_price=0
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Create order items from cart items, snapshotting the price
    total = 0
    for cart_item in cart.cart_items:
        product = cart_item.product
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=cart_item.quantity,
            price=product.price,  # price at time of purchase
        )
        db.add(order_item)
        total += product.price * cart_item.quantity

    order.total_price = total

    # Empty the cart
    for cart_item in cart.cart_items:
        db.delete(cart_item)

    db.commit()
    db.refresh(order)
    return order

def generate_order_number():
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD-{date_part}-{random_part}"