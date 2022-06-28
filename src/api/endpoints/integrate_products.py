import secrets
import os
import pandas as pd

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from dotenv import load_dotenv

from src.types import Route

router = APIRouter()
security = HTTPBasic()


@router.post("/")
async def integrate_products(file: UploadFile, credentials: HTTPBasicCredentials = Depends(security)):
    _validate(credentials)
    df = pd.read_csv(file.file, delimiter=",")
    shops = set(df["shop"].to_numpy())

    return {
        "shops": shops,
    }


def _validate(credentials: HTTPBasicCredentials):
    load_dotenv("credentials.env")
    correct_username = secrets.compare_digest(credentials.username, os.getenv("USERNAME"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("PASSWORD"))
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


route = Route(router=router, prefix="/integrate_products", tags=["Integrate Products"])
