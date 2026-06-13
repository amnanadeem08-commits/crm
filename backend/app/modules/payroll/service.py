from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.employees.models import Employee
from app.modules.auth.models import User
from app.modules.payroll.models import PayrollRecord
from app.modules.payroll.schemas import PayrollCreate


class PayrollService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: PayrollCreate, user: User) -> PayrollRecord:
        employee = self.db.scalar(select(Employee).where(Employee.id == payload.employee_id, Employee.shop_id == user.shop_id))
        if employee is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        net_salary = employee.monthly_salary - payload.advances - payload.deductions
        record = PayrollRecord(
            shop_id=user.shop_id,
            employee_id=payload.employee_id,
            payroll_month=payload.payroll_month,
            payroll_year=payload.payroll_year,
            base_salary=employee.monthly_salary,
            advances=payload.advances,
            deductions=payload.deductions,
            net_salary=net_salary,
            note=payload.note,
        )
        self.db.add(record)
        self.db.commit()
        return self.get(record.id, user)

    def list(self, user: User) -> list[PayrollRecord]:
        return list(
            self.db.scalars(
                select(PayrollRecord).options(selectinload(PayrollRecord.employee)).where(PayrollRecord.shop_id == user.shop_id).order_by(PayrollRecord.payroll_year.desc(), PayrollRecord.payroll_month.desc())
            )
        )

    def get(self, record_id: int, user: User) -> PayrollRecord:
        record = self.db.scalar(select(PayrollRecord).options(selectinload(PayrollRecord.employee)).where(PayrollRecord.id == record_id, PayrollRecord.shop_id == user.shop_id))
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payroll record not found")
        return record
