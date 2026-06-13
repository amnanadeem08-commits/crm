from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.modules.products.schemas import ProductRead


class RawMaterialCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    unit: str = Field(min_length=1, max_length=40)
    current_stock: Decimal = Field(default=0, ge=0)
    low_stock_threshold: Decimal = Field(default=0, ge=0)


class RawMaterialRead(RawMaterialCreate):
    id: int

    model_config = {"from_attributes": True}


class ProductionBatchCreate(BaseModel):
    batch_date: date
    finished_product_id: int
    quantity_produced: int = Field(gt=0)
    raw_material_cost: Decimal = Field(default=0, ge=0)
    wastage_quantity: int = Field(default=0, ge=0)
    note: str = ""


class ProductionBatchRead(BaseModel):
    id: int
    batch_date: date
    finished_product_id: int
    quantity_produced: int
    raw_material_cost: Decimal
    wastage_quantity: int
    note: str
    finished_product: ProductRead

    model_config = {"from_attributes": True}

