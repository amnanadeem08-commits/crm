from decimal import Decimal

from pydantic import BaseModel, Field


class EmployeeCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=3, max_length=40)
    role: str = Field(min_length=2, max_length=80)
    monthly_salary: Decimal = Field(default=0, ge=0)
    is_active: bool = True


class EmployeeUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, min_length=3, max_length=40)
    role: str | None = Field(default=None, min_length=2, max_length=80)
    monthly_salary: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None


class EmployeeRead(EmployeeCreate):
    id: int

    model_config = {"from_attributes": True}

