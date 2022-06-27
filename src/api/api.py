from fastapi import APIRouter

from src.api.endpoints import integrate_products


router = APIRouter()
router.include_router(transform.router, prefix="/transform", tags=["Transform"])
