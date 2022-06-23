from fastapi import APIRouter

from app.api.endpoints import products


router = APIRouter()
router.include_router(products.router, prefix="/products", tags=["Products"])
