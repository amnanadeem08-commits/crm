from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.finance.models import Expense
from app.modules.finance.schemas import ExpenseCreate, ProfitLossSummary
from app.modules.auth.models import User
from app.modules.payroll.models import PayrollRecord
from app.modules.sales.models import Sale


class FinanceService:
    def __init__(self, db: Session):
        self.db = db

    def create_expense(self, payload: ExpenseCreate, user: User) -> Expense:
        expense = Expense(shop_id=user.shop_id, **payload.model_dump())
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def list_expenses(self, user: User) -> list[Expense]:
        return list(self.db.scalars(select(Expense).where(Expense.shop_id == user.shop_id).order_by(Expense.expense_date.desc(), Expense.id.desc())))

    def profit_loss(self, user: User) -> ProfitLossSummary:
        sales = list(self.db.scalars(select(Sale).where(Sale.shop_id == user.shop_id)))
        payroll = list(self.db.scalars(select(PayrollRecord).where(PayrollRecord.shop_id == user.shop_id)))
        expenses = self.list_expenses(user)
        revenue = sum((row.total_revenue for row in sales), Decimal("0"))
        cost = sum((row.total_cost for row in sales), Decimal("0"))
        payroll_costs = sum((row.net_salary for row in payroll), Decimal("0"))
        expense_total = sum((row.amount for row in expenses), Decimal("0"))
        net_profit = revenue - cost - payroll_costs - expense_total
        return ProfitLossSummary(
            total_revenue=revenue,
            cost_of_goods=cost,
            payroll_costs=payroll_costs,
            expenses=expense_total,
            net_profit=net_profit,
            status="Profit" if net_profit >= 0 else "Loss",
        )
