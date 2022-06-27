from fastapi import APIRouter

from src.api.endpoints.transform import route


router = APIRouter()
router.include_router(route)
