from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.modules.products.models import Product


class RawMaterial(Base):
    __tablename__ = "raw_materials"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    unit: Mapped[str] = mapped_column(String(40), nullable=False)
    current_stock: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    low_stock_threshold: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)


class ProductionBatch(Base):
    __tablename__ = "production_batches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id"), nullable=False, index=True)
    batch_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    finished_product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity_produced: Mapped[int] = mapped_column(nullable=False)
    raw_material_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    wastage_quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    note: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    finished_product: Mapped[Product] = relationship()
