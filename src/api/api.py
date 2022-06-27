from fastapi import APIRouter

from src.api.endpoints import integrate_products


router = APIRouter()
router.include_router(integrate_products.router, prefix="/integrate_products", tags=["Product Integration"])
