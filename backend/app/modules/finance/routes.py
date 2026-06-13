from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import require_manager
from app.modules.auth.models import User
from app.modules.finance.schemas import ExpenseCreate, ExpenseRead, ProfitLossSummary
from app.modules.finance.service import FinanceService


router = APIRouter()


@router.post("/expenses", response_model=ExpenseRead, status_code=201)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db), _: User = Depends(require_manager)):
    return FinanceService(db).create_expense(payload)


@router.get("/expenses", response_model=list[ExpenseRead])
def list_expenses(db: Session = Depends(get_db), _: User = Depends(require_manager)):
    return FinanceService(db).list_expenses()


@router.get("/profit-loss", response_model=ProfitLossSummary)
def profit_loss(db: Session = Depends(get_db), _: User = Depends(require_manager)):
    return FinanceService(db).profit_loss()

