from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.category import CategoryUpdate, CreateCategory, CategoryResponse
from app.services.category_service import create_category, get_category_by_id, update_category, delete_category, get_all_categories

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def add_category(data: CreateCategory, db: Session = Depends(get_db)):
    category = create_category(db, data)
    return category

@router.get("/", response_model=list[CategoryResponse], status_code=status.HTTP_200_OK)
def get_categories(db: Session = Depends(get_db)):
    category = get_all_categories(db)
    return category

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_category(category_id: int, db: Session = Depends(get_db)):
    category = delete_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")


@router.put("/{category_id}", response_model=CategoryResponse)
def edit_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    category = update_category(db, category_id, data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
