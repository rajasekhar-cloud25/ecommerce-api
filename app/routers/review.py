from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from app.services.review_service import create_review, update_review, delete_review, get_product_reviews
from app.services.auth_dependency import get_current_user
from app.models.user import User
from fastapi.responses import RedirectResponse
from app.dependencies import get_current_user_or_redirect
from app.services.review_service import (
    has_user_purchased_product,
    has_user_reviewed_product,
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=ReviewResponse)
def create_user_review(data: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = create_review(db, current_user.id, data)
    return review

@router.get("/product/{product_id}", response_model=list[ReviewResponse])
def get_user_product_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = get_product_reviews(db, product_id)
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found")
    return reviews

@router.put("/{review_id}", response_model=ReviewResponse)
def update_user_review(review_id: int, data: ReviewUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = update_review(db, review_id, data)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_review(review_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = delete_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

@router.post("/add-form")
def add_review_form(
        product_id: int = Form(...),
        rating: float = Form(...),
        comment: str = Form(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_redirect),
):
    # Must have purchased
    if not has_user_purchased_product(db, current_user.id, product_id):
        return RedirectResponse(url=f"/product/{product_id}?review_error=must_buy", status_code=302)

    # Must not have reviewed already
    if has_user_reviewed_product(db, current_user.id, product_id):
        return RedirectResponse(url=f"/product/{product_id}?review_error=already_reviewed", status_code=302)

    # Validate rating
    if rating < 1 or rating > 5:
        return RedirectResponse(url=f"/product/{product_id}?review_error=invalid_rating", status_code=302)

    from app.schemas.review import ReviewCreate
    data = ReviewCreate(product_id=product_id, rating=rating, comment=comment)
    create_review(db, current_user.id, data)

    return RedirectResponse(url=f"/product/{product_id}?review=added", status_code=302)