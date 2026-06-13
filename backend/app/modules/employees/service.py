from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.employees.models import Employee
from app.modules.employees.schemas import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: EmployeeCreate) -> Employee:
        employee = Employee(**payload.model_dump())
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def list(self, active_only: bool = False) -> list[Employee]:
        query = select(Employee).order_by(Employee.full_name)
        if active_only:
            query = query.where(Employee.is_active.is_(True))
        return list(self.db.scalars(query))

    def get(self, employee_id: int) -> Employee:
        employee = self.db.get(Employee, employee_id)
        if employee is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        return employee

    def update(self, employee_id: int, payload: EmployeeUpdate) -> Employee:
        employee = self.get(employee_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(employee, key, value)
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def delete(self, employee_id: int) -> None:
        employee = self.get(employee_id)
        self.db.delete(employee)
        self.db.commit()

