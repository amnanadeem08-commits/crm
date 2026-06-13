from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.attendance.models import AttendanceRecord, AttendanceStatus
from app.modules.attendance.schemas import AttendanceCreate
from app.modules.employees.models import Employee


class AttendanceService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: AttendanceCreate) -> AttendanceRecord:
        if self.db.get(Employee, payload.employee_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        record = AttendanceRecord(**payload.model_dump())
        self.db.add(record)
        self.db.commit()
        return self.get(record.id)

    def list(self) -> list[AttendanceRecord]:
        return list(
            self.db.scalars(
                select(AttendanceRecord)
                .options(selectinload(AttendanceRecord.employee))
                .order_by(AttendanceRecord.work_date.desc(), AttendanceRecord.id.desc())
            )
        )

    def issues(self) -> list[AttendanceRecord]:
        return [row for row in self.list() if row.status in {AttendanceStatus.absent, AttendanceStatus.late}]

    def get(self, record_id: int) -> AttendanceRecord:
        record = self.db.scalar(
            select(AttendanceRecord).options(selectinload(AttendanceRecord.employee)).where(AttendanceRecord.id == record_id)
        )
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
        return record

