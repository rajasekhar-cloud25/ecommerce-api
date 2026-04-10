from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.cart_service import (
    get_all_cart_items,
    remove_cart_item,
    add_to_cart,
    update_cart_quantity,
)
from app.schemas.cart import AddToCart, CartItemResponse, CartResponse, UpdateQuantity
from app.dependencies import get_current_user, get_current_user_or_redirect
from app.models.user import User

router = APIRouter(prefix="/cart", tags=["Cart"])


# ===== JSON API endpoints =====

@router.post("/", response_model=CartItemResponse)
def add_item_to_cart(
        data: AddToCart,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return add_to_cart(db, current_user.id, data.product_id, data.quantity)


@router.get("/", response_model=CartResponse)
def get_cart(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    cart = get_all_cart_items(db, current_user.id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart Not Found")
    return cart


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(
        item_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    cart = remove_cart_item(db, item_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart item not found")


@router.put("/{item_id}", response_model=CartItemResponse)
def edit_cart_quantity(
        item_id: int,
        data: UpdateQuantity,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    cart_item = update_cart_quantity(db, item_id, data.quantity)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart Not Found")
    return cart_item


# ===== HTML form endpoints =====

@router.post("/add-form")
def add_to_cart_form(
        product_id: int = Form(...),
        quantity: int = Form(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_redirect),
):
    add_to_cart(db, current_user.id, product_id, quantity)
    return RedirectResponse(url="/cart?added=1", status_code=302)

@router.post("/remove-form")
def remove_cart_item_from(
    item_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_redirect)
):
    remove_cart_item(db, item_id)
    return RedirectResponse("/cart", status_code=302)