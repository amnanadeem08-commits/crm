from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.modules.products.schemas import ProductRead


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    note: str | None = None


class SaleCreate(BaseModel):
    customer_name: str = Field(default="Walk-in Customer", min_length=2, max_length=120)
    items: list[SaleItemCreate] = Field(min_length=1)


class SaleItemRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    unit_cost: Decimal
    note: str | None
    product: ProductRead

    model_config = {"from_attributes": True}


class SaleRead(BaseModel):
    id: int
    customer_name: str
    total_revenue: Decimal
    total_cost: Decimal
    created_at: datetime
    items: list[SaleItemRead]

    model_config = {"from_attributes": True}


class SalesReport(BaseModel):
    period: str
    total_sales: int
    total_revenue: Decimal
    total_cost: Decimal
    gross_profit: Decimal

