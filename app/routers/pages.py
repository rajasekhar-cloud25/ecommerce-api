from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.dependencies import get_current_user_or_redirect, get_optional_user
from app.models.user import User
from app.services.product_service import get_all_products, get_product_by_id,search_products
from app.services.cart_service import get_all_cart_items
from app.services.order_service import get_user_orders, get_order_by_id
from app.services.category_service import get_all_categories
from app.services.wishlist_service import get_wishlist
from app.services.address_service import get_user_addresses
from app.constants import COUNTRIES, US_STATES
from app.services.review_service import (
    get_product_reviews,
    get_product_rating_summary,
    has_user_purchased_product,
    has_user_reviewed_product,
)

router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory="templates")


def get_cart_count(db, user):
    """Helper: total items in cart for the navbar badge."""
    if not user:
        return 0
    cart = get_all_cart_items(db, user.id)
    if not cart or not cart.cart_items:
        return 0
    return sum(item.quantity for item in cart.cart_items)


@router.get("/")
def home_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user=Depends(get_optional_user),
        search: Optional[str] = None,
        category_id: Optional[str] = None,
        min_price: Optional[str] = None,
        max_price: Optional[str] = None,
        sort: Optional[str] = None,
):
    # Parse filter values from query string.
    # Empty strings come in when user submits the form without filling everything.
    category_filter = None
    if category_id:
        category_filter = int(category_id)

    min_price_filter = None
    if min_price:
        min_price_filter = float(min_price)

    max_price_filter = None
    if max_price:
        max_price_filter = float(max_price)

    products = search_products(
        db,
        search=search,
        category_id=category_filter,
        min_price=min_price_filter,
        max_price=max_price_filter,
        sort=sort,
    )

    categories = get_all_categories(db)

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "products": products,
            "categories": categories,
            "current_user": current_user,
            "cart_count": get_cart_count(db, current_user),
            "current_search": search or "",
            "current_category_id": category_filter,
            "current_min_price": min_price or "",
            "current_max_price": max_price or "",
            "current_sort": sort or "",
        },
    )


@router.get("/product/{product_id}")
def product_detail_page(
        product_id: int,
        request: Request,
        db: Session = Depends(get_db),
        current_user=Depends(get_optional_user),
):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    reviews = get_product_reviews(db, product_id)
    avg_rating, review_count = get_product_rating_summary(db, product_id)

    can_review = False
    already_reviewed = False
    if current_user:
        can_review = has_user_purchased_product(db, current_user.id, product_id)
        already_reviewed = has_user_reviewed_product(db, current_user.id, product_id)

    return templates.TemplateResponse(
        "product_detail.html",
        {
            "request": request,
            "product": product,
            "reviews": reviews,
            "avg_rating": avg_rating,
            "review_count": review_count,
            "can_review": can_review,
            "already_reviewed": already_reviewed,
            "current_user": current_user,
            "cart_count": get_cart_count(db, current_user),
        },
    )


@router.get("/cart")
def cart_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_redirect),
):
    cart = get_all_cart_items(db, current_user.id)

    total = 0
    if cart and cart.cart_items:
        for item in cart.cart_items:
            total += item.product.price * item.quantity

    return templates.TemplateResponse(
        "cart.html",
        {
            "request": request,
            "cart": cart,
            "total": total,
            "current_user": current_user,
            "cart_count": get_cart_count(db, current_user),
        },
    )


@router.get("/orders")
def orders_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_redirect),
):
    orders = get_user_orders(db, current_user.id)
    return templates.TemplateResponse(
        "orders.html",
        {
            "request": request,
            "orders": orders,
            "current_user": current_user,
            "cart_count": get_cart_count(db, current_user),
        },
    )


@router.get("/orders/{order_id}/view")
def order_detail_page(
        order_id: int,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_redirect),
):
    order = get_order_by_id(db, order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return templates.TemplateResponse(
        "order_detail.html",
        {
            "request": request,
            "order": order,
            "current_user": current_user,
            "cart_count": get_cart_count(db, current_user),
        },
    )

from app.services.wishlist_service import get_wishlist


@router.get("/wishlist")
def wishlist_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_redirect),
):
    items = get_wishlist(db, current_user.id)
    return templates.TemplateResponse(
        "wishlist.html",
        {
            "request": request,
            "items": items,
            "current_user": current_user,
            "cart_count": get_cart_count(db, current_user),
        },
    )

@router.get("/addresses")
def addresses_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_redirect),
):
    addresses = get_user_addresses(db, current_user.id)
    return templates.TemplateResponse(
        "addresses.html",
        {
            "request": request,
            "addresses": addresses,
            "current_user": current_user,
            "cart_count": get_cart_count(db, current_user),
            "countries": COUNTRIES,
            "us_states": US_STATES
        },
    )