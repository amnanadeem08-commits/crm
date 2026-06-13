from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import require_manager
from app.modules.auth.models import User
from app.modules.employees.schemas import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.modules.employees.service import EmployeeService


router = APIRouter()


@router.post("", response_model=EmployeeRead, status_code=201)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return EmployeeService(db).create(payload, current_user)


@router.get("", response_model=list[EmployeeRead])
def list_employees(active_only: bool = False, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return EmployeeService(db).list(current_user, active_only)


@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee(employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return EmployeeService(db).update(employee_id, payload, current_user)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    EmployeeService(db).delete(employee_id, current_user)
