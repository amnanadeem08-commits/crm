from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import require_manager
from app.modules.auth.models import User
from app.modules.payroll.schemas import PayrollCreate, PayrollRead
from app.modules.payroll.service import PayrollService


router = APIRouter()


@router.post("", response_model=PayrollRead, status_code=201)
def create_payroll(payload: PayrollCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return PayrollService(db).create(payload, current_user)


@router.get("", response_model=list[PayrollRead])
def list_payroll(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return PayrollService(db).list(current_user)
