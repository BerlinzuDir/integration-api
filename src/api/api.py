from fastapi import APIRouter

from src.api.endpoints import transform


router = APIRouter()
router.include_router(transform.router, prefix="/transform", tags=["Transform"])
