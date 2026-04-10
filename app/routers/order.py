from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import stripe
from app.services.email_service import send_order_confirmation_email, send_order_status_email

from app.database import get_db
from app.config import settings
from app.schemas.order import OrderCreate, OrderResponse, UpdateOrderStatus
from app.services.order_service import (
    create_order,
    get_user_orders,
    get_order_by_id,
    update_order_status,
    cancel_order,
    checkout_cart,
)
from app.services.cart_service import get_all_cart_items
from app.services.auth_dependency import get_current_user
from app.dependencies import get_current_user_or_redirect
from app.models.user import User

# Configure Stripe
stripe.api_key = settings.stripe_secret_key

router = APIRouter(prefix="/orders", tags=["Orders"])


# ===== HTML form endpoints (Stripe checkout flow) =====
# IMPORTANT: These must be declared BEFORE /{order_id} routes
# otherwise "stripe-success" gets matched as an order_id parameter

@router.post("/checkout-form")
def checkout_form(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_redirect),
):
    # Get user's cart
    cart = get_all_cart_items(db, current_user.id)
    if not cart or not cart.cart_items:
        return RedirectResponse(url="/cart?error=empty", status_code=302)

    # Make sure user has a default address
    from app.services.address_service import get_user_addresses
    addresses = get_user_addresses(db, current_user.id)
    default_address = None
    for addr in addresses:
        if addr.is_default:
            default_address = addr
            break

    if not default_address:
        return RedirectResponse(url="/addresses?error=no_default", status_code=302)

    # Build Stripe line items from cart
    line_items = []
    for item in cart.cart_items:
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": item.product.title,
                    "description": item.product.brand or "",
                    "images": [item.product.images] if item.product.images else [],
                },
                "unit_amount": int(item.product.price * 100),  # Stripe uses cents
            },
            "quantity": item.quantity,
        })

    # Create Stripe Checkout Session
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=settings.stripe_success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.stripe_cancel_url,
            metadata={
                "user_id": str(current_user.id),
                "address_id": str(default_address.id)
            },
        )
    except Exception as e:
        print(f"Stripe error: {e}")
        return RedirectResponse(url="/cart?error=stripe", status_code=302)

    # Redirect user to Stripe hosted checkout page
    return RedirectResponse(url=session.url, status_code=303)


@router.get("/stripe-success")
def stripe_success(
        session_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_redirect),
):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        print(f"Stripe retrieve error: {e}")
        return RedirectResponse(url="/cart?error=verify", status_code=302)

    if session.payment_status != "paid":
        return RedirectResponse(url="/cart?error=unpaid", status_code=302)

    # Pull the address from Stripe metadata (we set it during checkout)
    address_id = None
    try:
        if session.metadata and "address_id" in session.metadata:
            address_id = int(session.metadata["address_id"])
    except Exception as e:
        print(f"Could not parse address_id from metadata: {e}")

    # Payment verified — create the actual order
    order = checkout_cart(db, current_user.id, address_id=address_id)
    if not order:
        return RedirectResponse(url="/orders?error=empty", status_code=302)

    # Mark as confirmed and save Stripe payment intent for refunds
    order.status = "confirmed"
    order.stripe_payment_intent = session.payment_intent
    db.commit()
    db.refresh(order)

    # Send order confirmation email
    send_order_confirmation_email(
        to=current_user.email,
        name=current_user.name,
        order_number=order.order_number,
        total=order.total_price,
        items=order.order_items,
    )

    return RedirectResponse(url=f"/orders/{order.id}/view", status_code=302)


# ===== JSON API endpoints =====

@router.post("/", response_model=OrderResponse)
def place_order(
        data: OrderCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return create_order(db, current_user.id, data)


@router.get("/", response_model=list[OrderResponse])
def get_my_orders(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    orders = get_user_orders(db, current_user.id)
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
        order_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}/cancel", response_model=OrderResponse)
def cancel_user_order(
        order_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    order = cancel_order(db, order_id)
    if order is False:
        raise HTTPException(status_code=400, detail="Cannot cancel shipped or delivered order")
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}", response_model=OrderResponse)
def update_status(
        order_id: int,
        data: UpdateOrderStatus,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    order = update_order_status(db, order_id, data.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order