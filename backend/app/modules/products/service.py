from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.products.models import Product, ProductCategory
from app.modules.products.schemas import CategoryCreate, ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def create_category(self, payload: CategoryCreate) -> ProductCategory:
        existing = self.db.scalar(select(ProductCategory).where(ProductCategory.name == payload.name.strip()))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
        category = ProductCategory(name=payload.name.strip(), description=payload.description)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def list_categories(self) -> list[ProductCategory]:
        return list(self.db.scalars(select(ProductCategory).order_by(ProductCategory.name)))

    def create_product(self, payload: ProductCreate) -> Product:
        self._ensure_unique_sku(payload.sku)
        if payload.category_id is not None:
            self._get_category(payload.category_id)
        product = Product(**payload.model_dump())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return self.get_product(product.id)

    def list_products(self, active_only: bool = False) -> list[Product]:
        query = select(Product).options(selectinload(Product.category)).order_by(Product.name)
        if active_only:
            query = query.where(Product.is_active.is_(True))
        return list(self.db.scalars(query))

    def get_product(self, product_id: int) -> Product:
        product = self.db.scalar(
            select(Product).options(selectinload(Product.category)).where(Product.id == product_id)
        )
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    def update_product(self, product_id: int, payload: ProductUpdate) -> Product:
        product = self.get_product(product_id)
        changes = payload.model_dump(exclude_unset=True)
        if "sku" in changes and changes["sku"] != product.sku:
            self._ensure_unique_sku(changes["sku"])
        if "category_id" in changes and changes["category_id"] is not None:
            self._get_category(changes["category_id"])
        cost_price = changes.get("cost_price", product.cost_price)
        selling_price = changes.get("selling_price", product.selling_price)
        if selling_price < cost_price:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Selling price cannot be lower than cost price")
        for key, value in changes.items():
            setattr(product, key, value)
        self.db.commit()
        return self.get_product(product.id)

    def delete_product(self, product_id: int) -> None:
        product = self.get_product(product_id)
        self.db.delete(product)
        self.db.commit()

    def _ensure_unique_sku(self, sku: str) -> None:
        existing = self.db.scalar(select(Product).where(Product.sku == sku.strip()))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already exists")

    def _get_category(self, category_id: int) -> ProductCategory:
        category = self.db.get(ProductCategory, category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return category

