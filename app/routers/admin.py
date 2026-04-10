from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.services.email_service import send_order_status_email
from app.database import get_db
from app.dependencies import get_admin_user_or_redirect
from app.models.user import User
from app.models.order import Order
from app.models.product import Product
from app.services.order_service import update_order_status
from app.services.product_service import get_all_products
import stripe
from app.config import settings
stripe.api_key = settings.stripe_secret_key

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="templates")


@router.get("")
def admin_dashboard(
        request: Request,
        db: Session = Depends(get_db),
        admin: User = Depends(get_admin_user_or_redirect),
):
    total_products = db.query(Product).count()
    total_orders = db.query(Order).count()
    total_users = db.query(User).count()
    pending_orders = db.query(Order).filter(Order.status == "pending").count()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "current_user": admin,
            "cart_count": 0,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_users": total_users,
            "pending_orders": pending_orders,
        },
    )


@router.get("/orders")
def admin_orders(
        request: Request,
        db: Session = Depends(get_db),
        admin: User = Depends(get_admin_user_or_redirect),
):
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin/orders.html",
        {
            "request": request,
            "current_user": admin,
            "cart_count": 0,
            "orders": orders,
        },
    )


@router.post("/orders/{order_id}/update-status")
def admin_update_order_status(
        order_id: int,
        status: str = Form(...),
        db: Session = Depends(get_db),
        admin: User = Depends(get_admin_user_or_redirect),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return RedirectResponse(url="/admin/orders?error=not_found", status_code=302)
    update_order_status(db, order_id, status)

    # Send status email to the customer
    customer = db.query(User).filter(User.id == order.user_id).first()
    if customer:
        send_order_status_email(
            to=customer.email,
            name=customer.name,
            order_number=order.order_number,
            new_status=status,
        )

    return RedirectResponse(url="/admin/orders", status_code=302)


@router.get("/products")
def admin_products(
        request: Request,
        db: Session = Depends(get_db),
        admin: User = Depends(get_admin_user_or_redirect),
):
    products = get_all_products(db)
    return templates.TemplateResponse(
        "admin/products.html",
        {
            "request": request,
            "current_user": admin,
            "cart_count": 0,
            "products": products,
        },
    )


@router.get("/users")
def admin_users(
        request: Request,
        db: Session = Depends(get_db),
        admin: User = Depends(get_admin_user_or_redirect),
):
    users = db.query(User).all()
    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "current_user": admin,
            "cart_count": 0,
            "users": users,
        },
    )

@router.post("/orders/{order_id}/refund")
def admin_refund_order(
        order_id: int,
        db: Session = Depends(get_db),
        admin: User = Depends(get_admin_user_or_redirect),
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        return RedirectResponse(url="/admin/orders?error=not_found", status_code=302)

    # Can't refund already-refunded or cancelled orders
    if order.status in ["refunded", "cancelled"]:
        return RedirectResponse(url="/admin/orders?error=already_refunded", status_code=302)

    # Can't refund without a payment intent (e.g. orders created before Stripe)
    if not order.stripe_payment_intent:
        return RedirectResponse(url="/admin/orders?error=no_payment", status_code=302)

    # Issue refund through Stripe
    try:
        stripe.Refund.create(payment_intent=order.stripe_payment_intent)
    except Exception as e:
        print(f"Refund error: {e}")
        return RedirectResponse(url="/admin/orders?error=stripe", status_code=302)

    # Mark order as refunded
    order.status = "refunded"
    db.commit()

    # Send refund email
    customer = db.query(User).filter(User.id == order.user_id).first()
    if customer:
        send_order_status_email(
            to=customer.email,
            name=customer.name,
            order_number=order.order_number,
            new_status="refunded",
        )

    return RedirectResponse(url="/admin/orders?refunded=1", status_code=302)

