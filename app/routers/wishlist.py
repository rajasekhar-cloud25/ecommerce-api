from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.wishlist import AddToWishlist, WishlistResponse
from app.services.wishlist_service import get_wishlist, add_to_wishlist, remove_from_wishlist
from app.services.auth_dependency import get_current_user
from app.models.user import User
from fastapi import Form
from fastapi.responses import RedirectResponse
from app.dependencies import get_current_user_or_redirect

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

@router.post("/", response_model=WishlistResponse)
def add_item_to_wishlist(data: AddToWishlist, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wishlist = add_to_wishlist(db, current_user.id, data.product_id)
    return wishlist

@router.post("/add-form")
def add_to_wishlist_form(
        db: Session = Depends(get_db),
        product_id: int = Form(...),
        current_user: User = Depends(get_current_user_or_redirect)
):
    add_to_wishlist(db, current_user.id, product_id)
    return RedirectResponse(url=f"/product/{product_id}?wishlist=added", status_code=302)

@router.post("/remove-form")
def remove_from_wishlist_form(
        db: Session = Depends(get_db),
        item_id: int = Form(...),
        current_user: User = Depends(get_current_user_or_redirect)
):
    remove_from_wishlist(db, item_id)
    return RedirectResponse(url="/wishlist", status_code=302)

@router.get("/", response_model=list[WishlistResponse])
def get_user_wishlist(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wishlist = get_wishlist(db, current_user.id)
    return wishlist

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_from_wishlist(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = remove_from_wishlist(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")