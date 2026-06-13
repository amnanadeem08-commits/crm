from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import require_manager
from app.modules.auth.models import User
from app.modules.sales.schemas import SaleCreate, SaleRead, SalesReport
from app.modules.sales.service import SalesService


router = APIRouter()


@router.post("", response_model=SaleRead, status_code=201)
def create_sale(payload: SaleCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return SalesService(db).create(payload, current_user)


@router.get("", response_model=list[SaleRead])
def list_sales(customer_name: str | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return SalesService(db).list(current_user, customer_name)


@router.get("/reports/{period}", response_model=SalesReport)
def sales_report(period: str, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return SalesService(db).report(period, current_user)
