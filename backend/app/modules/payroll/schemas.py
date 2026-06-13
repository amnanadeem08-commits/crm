from decimal import Decimal

from pydantic import BaseModel, Field

from app.modules.employees.schemas import EmployeeRead


class PayrollCreate(BaseModel):
    employee_id: int
    payroll_month: int = Field(ge=1, le=12)
    payroll_year: int = Field(ge=2000, le=2100)
    advances: Decimal = Field(default=0, ge=0)
    deductions: Decimal = Field(default=0, ge=0)
    note: str = ""


class PayrollRead(BaseModel):
    id: int
    shop_id: int
    employee_id: int
    payroll_month: int
    payroll_year: int
    base_salary: Decimal
    advances: Decimal
    deductions: Decimal
    net_salary: Decimal
    note: str
    employee: EmployeeRead

    model_config = {"from_attributes": True}
