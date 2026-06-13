from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    expense_date: date
    category: str = Field(min_length=2, max_length=80)
    amount: Decimal = Field(gt=0)
    note: str = ""


class ExpenseRead(ExpenseCreate):
    id: int

    model_config = {"from_attributes": True}


class ProfitLossSummary(BaseModel):
    total_revenue: Decimal
    cost_of_goods: Decimal
    payroll_costs: Decimal
    expenses: Decimal
    net_profit: Decimal
    status: str

