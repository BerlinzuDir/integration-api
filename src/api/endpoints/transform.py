from typing import Dict

from fastapi import APIRouter

router = APIRouter()


@router.post("/", response_model=Dict[str, str])
async def transform(products: Dict):
    return products
