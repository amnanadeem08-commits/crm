from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.auth.models import User
from app.modules.inventory.models import MovementType
from app.modules.inventory.schemas import MovementCreate
from app.modules.inventory.service import InventoryService
from app.modules.products.models import Product
from app.modules.sales.models import Sale, SaleItem
from app.modules.sales.schemas import SaleCreate, SalesReport


class SalesService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: SaleCreate, user: User) -> Sale:
        total_revenue = Decimal("0")
        total_cost = Decimal("0")
        sale_items: list[SaleItem] = []

        for item in payload.items:
            product = self.db.scalar(select(Product).where(Product.id == item.product_id, Product.shop_id == user.shop_id))
            if product is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
            total_revenue += item.unit_price * item.quantity
            total_cost += product.cost_price * item.quantity
            sale_items.append(
                SaleItem(
                    shop_id=user.shop_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    unit_cost=product.cost_price,
                    note=item.note,
                )
            )

        sale = Sale(shop_id=user.shop_id, customer_name=payload.customer_name, total_revenue=total_revenue, total_cost=total_cost, items=sale_items)
        self.db.add(sale)
        self.db.flush()

        inventory = InventoryService(self.db)
        for item in payload.items:
            inventory.create_movement(
                MovementCreate(product_id=item.product_id, movement_type=MovementType.sale, quantity=item.quantity, note=f"Sale #{sale.id}"),
                user,
            )
        self.db.commit()
        return self.get(sale.id, user)

    def list(self, user: User, customer_name: str | None = None) -> list[Sale]:
        query = (
            select(Sale)
            .options(selectinload(Sale.items).selectinload(SaleItem.product).selectinload(Product.category))
            .where(Sale.shop_id == user.shop_id)
            .order_by(Sale.created_at.desc())
        )
        if customer_name:
            query = query.where(Sale.customer_name.ilike(f"%{customer_name}%"))
        return list(self.db.scalars(query))

    def get(self, sale_id: int, user: User) -> Sale:
        sale = self.db.scalar(
            select(Sale)
            .options(selectinload(Sale.items).selectinload(SaleItem.product).selectinload(Product.category))
            .where(Sale.id == sale_id, Sale.shop_id == user.shop_id)
        )
        if sale is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
        return sale

    def report(self, period: str, user: User) -> SalesReport:
        start = self._period_start(period)
        rows = [row for row in self.list(user) if row.created_at >= start]
        revenue = sum((row.total_revenue for row in rows), Decimal("0"))
        cost = sum((row.total_cost for row in rows), Decimal("0"))
        return SalesReport(period=period, total_sales=len(rows), total_revenue=revenue, total_cost=cost, gross_profit=revenue - cost)

    @staticmethod
    def _period_start(period: str) -> datetime:
        now = datetime.utcnow()
        if period == "daily":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        if period == "weekly":
            return now - timedelta(days=7)
        if period == "monthly":
            return now - timedelta(days=30)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Period must be daily, weekly, or monthly")
