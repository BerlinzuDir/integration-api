import secrets
import os
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from dotenv import load_dotenv

from src.types import Route

router = APIRouter()
security = HTTPBasic()


def validate(credentials: HTTPBasicCredentials):
    load_dotenv("credentials.env")
    correct_username = secrets.compare_digest(credentials.username, os.getenv("LOGIN"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("PASSWORD"))
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )


@router.post("/")
def transform(products: Dict, credentials: HTTPBasicCredentials = Depends(security)):
    validate(credentials)
    return {
        "products": products,
    }


route = Route(router=router, prefix="/transform", tags=["Transform"])
