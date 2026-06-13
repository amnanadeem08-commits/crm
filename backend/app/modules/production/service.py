from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.auth.models import User
from app.modules.inventory.models import MovementType
from app.modules.inventory.schemas import MovementCreate
from app.modules.inventory.service import InventoryService
from app.modules.products.models import Product
from app.modules.production.models import ProductionBatch, RawMaterial
from app.modules.production.schemas import ProductionBatchCreate, RawMaterialCreate


class ProductionService:
    def __init__(self, db: Session):
        self.db = db

    def create_material(self, payload: RawMaterialCreate, user: User) -> RawMaterial:
        material = RawMaterial(shop_id=user.shop_id, **payload.model_dump())
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)
        return material

    def list_materials(self, user: User) -> list[RawMaterial]:
        return list(self.db.scalars(select(RawMaterial).where(RawMaterial.shop_id == user.shop_id).order_by(RawMaterial.name)))

    def create_batch(self, payload: ProductionBatchCreate, user: User) -> ProductionBatch:
        product = self.db.scalar(select(Product).where(Product.id == payload.finished_product_id, Product.shop_id == user.shop_id))
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finished product not found")
        batch = ProductionBatch(shop_id=user.shop_id, **payload.model_dump())
        self.db.add(batch)
        self.db.flush()
        InventoryService(self.db).create_movement(
            MovementCreate(
                product_id=payload.finished_product_id,
                movement_type=MovementType.production_in,
                quantity=payload.quantity_produced,
                note=f"Production batch #{batch.id}",
            ),
            user,
        )
        self.db.commit()
        return self.get_batch(batch.id, user)

    def list_batches(self, user: User) -> list[ProductionBatch]:
        return list(
            self.db.scalars(
                select(ProductionBatch)
                .options(selectinload(ProductionBatch.finished_product).selectinload(Product.category))
                .where(ProductionBatch.shop_id == user.shop_id)
                .order_by(ProductionBatch.batch_date.desc(), ProductionBatch.id.desc())
            )
        )

    def get_batch(self, batch_id: int, user: User) -> ProductionBatch:
        batch = self.db.scalar(
            select(ProductionBatch)
            .options(selectinload(ProductionBatch.finished_product).selectinload(Product.category))
            .where(ProductionBatch.id == batch_id, ProductionBatch.shop_id == user.shop_id)
        )
        if batch is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production batch not found")
        return batch
