from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.attendance.schemas import AttendanceCreate, AttendanceRead
from app.modules.attendance.service import AttendanceService
from app.modules.auth.dependencies import require_manager
from app.modules.auth.models import User


router = APIRouter()


@router.post("", response_model=AttendanceRead, status_code=201)
def create_attendance(payload: AttendanceCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return AttendanceService(db).create(payload, current_user)


@router.get("", response_model=list[AttendanceRead])
def list_attendance(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return AttendanceService(db).list(current_user)


@router.get("/issues", response_model=list[AttendanceRead])
def attendance_issues(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return AttendanceService(db).issues(current_user)
