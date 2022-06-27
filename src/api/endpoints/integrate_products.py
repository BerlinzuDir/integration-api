from typing import Dict

from fastapi import APIRouter

router = APIRouter()


@router.post("/", response_model=Dict[str, str])
async def integrate_products(products: Dict):
    return products
