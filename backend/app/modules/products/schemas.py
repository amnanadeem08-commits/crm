from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None


class CategoryRead(CategoryCreate):
    id: int
    shop_id: int

    model_config = {"from_attributes": True}


class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    sku: str = Field(min_length=2, max_length=80)
    cost_price: Decimal = Field(ge=0)
    selling_price: Decimal = Field(ge=0)
    category_id: int | None = None
    is_active: bool = True

    @model_validator(mode="after")
    def selling_price_covers_cost(self):
        if self.selling_price < self.cost_price:
            raise ValueError("Selling price cannot be lower than cost price")
        return self


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    sku: str | None = Field(default=None, min_length=2, max_length=80)
    cost_price: Decimal | None = Field(default=None, ge=0)
    selling_price: Decimal | None = Field(default=None, ge=0)
    category_id: int | None = None
    is_active: bool | None = None


class ProductRead(ProductBase):
    id: int
    shop_id: int
    category: CategoryRead | None = None

    model_config = {"from_attributes": True}
