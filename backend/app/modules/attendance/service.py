from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.attendance.models import AttendanceRecord, AttendanceStatus
from app.modules.attendance.schemas import AttendanceCreate
from app.modules.auth.models import User
from app.modules.employees.models import Employee


class AttendanceService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: AttendanceCreate, user: User) -> AttendanceRecord:
        employee = self.db.scalar(select(Employee).where(Employee.id == payload.employee_id, Employee.shop_id == user.shop_id))
        if employee is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        record = AttendanceRecord(shop_id=user.shop_id, **payload.model_dump())
        self.db.add(record)
        self.db.commit()
        return self.get(record.id, user)

    def list(self, user: User) -> list[AttendanceRecord]:
        return list(
            self.db.scalars(
                select(AttendanceRecord)
                .options(selectinload(AttendanceRecord.employee))
                .where(AttendanceRecord.shop_id == user.shop_id)
                .order_by(AttendanceRecord.work_date.desc(), AttendanceRecord.id.desc())
            )
        )

    def issues(self, user: User) -> list[AttendanceRecord]:
        return [row for row in self.list(user) if row.status in {AttendanceStatus.absent, AttendanceStatus.late}]

    def get(self, record_id: int, user: User) -> AttendanceRecord:
        record = self.db.scalar(
            select(AttendanceRecord).options(selectinload(AttendanceRecord.employee)).where(AttendanceRecord.id == record_id, AttendanceRecord.shop_id == user.shop_id)
        )
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
        return record
