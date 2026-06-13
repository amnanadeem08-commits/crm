from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.modules.auth.routes import router as auth_router
from app.modules.products.routes import router as products_router
from app.modules.inventory.routes import router as inventory_router
from app.modules.ai.routes import router as ai_router
from app.modules.employees.routes import router as employees_router
from app.modules.attendance.routes import router as attendance_router
from app.modules.sales.routes import router as sales_router
from app.modules.payroll.routes import router as payroll_router
from app.modules.finance.routes import router as finance_router
from app.modules.production.routes import router as production_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name}


app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products_router, prefix="/api/v1/products", tags=["products"])
app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["inventory"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(employees_router, prefix="/api/v1/employees", tags=["employees"])
app.include_router(attendance_router, prefix="/api/v1/attendance", tags=["attendance"])
app.include_router(sales_router, prefix="/api/v1/sales", tags=["sales"])
app.include_router(payroll_router, prefix="/api/v1/payroll", tags=["payroll"])
app.include_router(finance_router, prefix="/api/v1/finance", tags=["finance"])
app.include_router(production_router, prefix="/api/v1/production", tags=["production"])
