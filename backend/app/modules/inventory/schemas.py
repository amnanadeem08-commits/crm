from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.inventory.models import MovementType
from app.modules.products.schemas import ProductRead


class StockUpsert(BaseModel):
    product_id: int
    current_stock: int = Field(ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)


class StockRead(BaseModel):
    id: int
    product_id: int
    current_stock: int
    low_stock_threshold: int
    product: ProductRead

    model_config = {"from_attributes": True}


class MovementCreate(BaseModel):
    product_id: int
    movement_type: MovementType
    quantity: int = Field(gt=0)
    note: str | None = None


class MovementRead(BaseModel):
    id: int
    product_id: int
    movement_type: MovementType
    quantity: int
    note: str | None
    created_at: datetime
    product: ProductRead

    model_config = {"from_attributes": True}

