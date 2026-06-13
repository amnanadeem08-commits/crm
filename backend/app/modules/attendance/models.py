from datetime import date, datetime, time
from enum import Enum
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, Time
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.modules.employees.models import Employee


class AttendanceStatus(str, Enum):
    present = "present"
    late = "late"
    absent = "absent"


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id"), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    work_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[AttendanceStatus] = mapped_column(SqlEnum(AttendanceStatus), nullable=False)
    check_in: Mapped[Optional[time]] = mapped_column(Time)
    note: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    employee: Mapped[Employee] = relationship()
