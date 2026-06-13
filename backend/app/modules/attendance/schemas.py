from datetime import date, time

from pydantic import BaseModel

from app.modules.attendance.models import AttendanceStatus
from app.modules.employees.schemas import EmployeeRead


class AttendanceCreate(BaseModel):
    employee_id: int
    work_date: date
    status: AttendanceStatus
    check_in: time | None = None
    note: str | None = None


class AttendanceRead(AttendanceCreate):
    id: int
    shop_id: int
    employee: EmployeeRead

    model_config = {"from_attributes": True}
