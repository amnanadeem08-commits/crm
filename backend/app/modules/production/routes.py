from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import require_manager
from app.modules.auth.models import User
from app.modules.production.schemas import ProductionBatchCreate, ProductionBatchRead, RawMaterialCreate, RawMaterialRead
from app.modules.production.service import ProductionService


router = APIRouter()


@router.post("/raw-materials", response_model=RawMaterialRead, status_code=201)
def create_material(payload: RawMaterialCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return ProductionService(db).create_material(payload, current_user)


@router.get("/raw-materials", response_model=list[RawMaterialRead])
def list_materials(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return ProductionService(db).list_materials(current_user)


@router.post("/batches", response_model=ProductionBatchRead, status_code=201)
def create_batch(payload: ProductionBatchCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return ProductionService(db).create_batch(payload, current_user)


@router.get("/batches", response_model=list[ProductionBatchRead])
def list_batches(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return ProductionService(db).list_batches(current_user)
