from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_current_user
from app.models.product import Product
from app.models.user import User
from app.database import get_db
from app.schemas.product import ProductResponse, ProductUpdate, CreateProduct
from app.services.product_service import create_product, get_all_products, get_product_by_id, delete_product, update_product

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def add_product(
        data: CreateProduct,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return create_product(db, data)

@router.get("/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def get_products(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return get_all_products(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
        product_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_product(
        product_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    product = delete_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def edit_product(
        product_id: int,
        data: ProductUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    product = update_product(db, product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product