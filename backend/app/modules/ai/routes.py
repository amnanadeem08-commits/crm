from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.ai.schemas import BusinessException, BusinessHealth, BusinessInsight, DailyBrief
from app.modules.ai.service import AiInsightService
from app.modules.auth.dependencies import require_manager
from app.modules.auth.models import User
from app.modules.inventory.service import InventoryService


router = APIRouter()


@router.get("/inventory-insight", response_model=BusinessInsight)
def inventory_insight(db: Session = Depends(get_db), _: User = Depends(require_manager)):
    stock_rows = InventoryService(db).list_stock()
    return AiInsightService().inventory_insight(stock_rows)


@router.get("/business-health", response_model=BusinessHealth)
def business_health(db: Session = Depends(get_db), _: User = Depends(require_manager)):
    inventory = InventoryService(db)
    return AiInsightService().business_health(inventory.list_stock(), inventory.list_movements())


@router.get("/exceptions", response_model=list[BusinessException])
def exceptions(db: Session = Depends(get_db), _: User = Depends(require_manager)):
    inventory = InventoryService(db)
    return AiInsightService().detect_exceptions(inventory.list_stock(), inventory.list_movements())


@router.get("/daily-brief", response_model=DailyBrief)
def daily_brief(db: Session = Depends(get_db), _: User = Depends(require_manager)):
    inventory = InventoryService(db)
    return AiInsightService().daily_brief(inventory.list_stock(), inventory.list_movements())
