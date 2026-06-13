from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.auth.models import User
from app.modules.inventory.models import InventoryStock, MovementType, StockMovement
from app.modules.inventory.schemas import MovementCreate, StockUpsert
from app.modules.products.models import Product


class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def upsert_stock(self, payload: StockUpsert) -> InventoryStock:
        self._get_product(payload.product_id)
        stock = self.db.scalar(select(InventoryStock).where(InventoryStock.product_id == payload.product_id))
        if stock is None:
            stock = InventoryStock(**payload.model_dump())
            self.db.add(stock)
        else:
            stock.current_stock = payload.current_stock
            stock.low_stock_threshold = payload.low_stock_threshold
        self.db.commit()
        return self._get_stock_by_product(payload.product_id)

    def list_stock(self) -> list[InventoryStock]:
        return list(
            self.db.scalars(
                select(InventoryStock)
                .options(selectinload(InventoryStock.product).selectinload(Product.category))
                .join(Product)
                .order_by(Product.name)
            )
        )

    def low_stock_alerts(self) -> list[InventoryStock]:
        return [stock for stock in self.list_stock() if stock.current_stock <= stock.low_stock_threshold]

    def create_movement(self, payload: MovementCreate, user: User) -> StockMovement:
        self._get_product(payload.product_id)
        stock = self._get_stock_by_product(payload.product_id)
        new_level = self._apply_quantity(stock.current_stock, payload.movement_type, payload.quantity)
        if new_level < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Stock cannot go below zero")

        movement = StockMovement(
            product_id=payload.product_id,
            movement_type=payload.movement_type,
            quantity=payload.quantity,
            note=payload.note,
            created_by_id=user.id,
        )
        stock.current_stock = new_level
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)
        return self.get_movement(movement.id)

    def list_movements(self, product_id: int | None = None) -> list[StockMovement]:
        query = (
            select(StockMovement)
            .options(selectinload(StockMovement.product).selectinload(Product.category))
            .order_by(StockMovement.created_at.desc())
        )
        if product_id is not None:
            query = query.where(StockMovement.product_id == product_id)
        return list(self.db.scalars(query))

    def get_movement(self, movement_id: int) -> StockMovement:
        movement = self.db.scalar(
            select(StockMovement)
            .options(selectinload(StockMovement.product).selectinload(Product.category))
            .where(StockMovement.id == movement_id)
        )
        if movement is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movement not found")
        return movement

    def _get_stock_by_product(self, product_id: int) -> InventoryStock:
        stock = self.db.scalar(
            select(InventoryStock)
            .options(selectinload(InventoryStock.product).selectinload(Product.category))
            .where(InventoryStock.product_id == product_id)
        )
        if stock is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock record not found for product")
        return stock

    def _get_product(self, product_id: int) -> Product:
        product = self.db.get(Product, product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    @staticmethod
    def _apply_quantity(current_stock: int, movement_type: MovementType, quantity: int) -> int:
        if movement_type in {MovementType.purchase, MovementType.production_in}:
            return current_stock + quantity
        return current_stock - quantity

