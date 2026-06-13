from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import require_manager
from app.modules.auth.models import User
from app.modules.products.schemas import CategoryCreate, CategoryRead, ProductCreate, ProductRead, ProductUpdate
from app.modules.products.service import ProductService


router = APIRouter()


@router.post("/categories", response_model=CategoryRead, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), _: User = Depends(require_manager)):
    return ProductService(db).create_category(payload)


@router.get("/categories", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db), _: User = Depends(require_manager)):
    return ProductService(db).list_categories()


@router.post("", response_model=ProductRead, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), _: User = Depends(require_manager)):
    return ProductService(db).create_product(payload)


@router.get("", response_model=list[ProductRead])
def list_products(active_only: bool = False, db: Session = Depends(get_db), _: User = Depends(require_manager)):
    return ProductService(db).list_products(active_only=active_only)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(require_manager)):
    return ProductService(db).get_product(product_id)


@router.put("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), _: User = Depends(require_manager)):
    return ProductService(db).update_product(product_id, payload)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(require_manager)):
    ProductService(db).delete_product(product_id)

