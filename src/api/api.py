from fastapi import APIRouter


from src.api.endpoints.integrate_products import route


router = APIRouter()
router.include_router(**route)
