from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import require_manager
from app.modules.auth.models import User
from app.modules.inventory.schemas import MovementCreate, MovementRead, StockRead, StockUpsert
from app.modules.inventory.service import InventoryService


router = APIRouter()


@router.post("/stock", response_model=StockRead, status_code=201)
def upsert_stock(payload: StockUpsert, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return InventoryService(db).upsert_stock(payload, current_user)


@router.get("/stock", response_model=list[StockRead])
def list_stock(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return InventoryService(db).list_stock(current_user)


@router.get("/alerts/low-stock", response_model=list[StockRead])
def low_stock_alerts(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return InventoryService(db).low_stock_alerts(current_user)


@router.post("/movements", response_model=MovementRead, status_code=201)
def create_movement(payload: MovementCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return InventoryService(db).create_movement(payload, current_user)


@router.get("/movements", response_model=list[MovementRead])
def list_movements(
    product_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return InventoryService(db).list_movements(_, product_id=product_id)
