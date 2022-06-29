import json
import secrets
import os
import pandas as pd
import requests

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from dotenv import load_dotenv

from src.types import Route

router = APIRouter()
security = HTTPBasic()
load_dotenv()


@router.post("/")
async def integrate_products(file: UploadFile, credentials: HTTPBasicCredentials = Depends(security)):
    _validate_credentials(credentials)
    df = _to_dataframe(file)
    _validate_data(df)
    _send_to_lozuka(data=df.to_json())
    return {
        "shops": "dings",
    }


def _validate_credentials(credentials: HTTPBasicCredentials):
    correct_username = secrets.compare_digest(credentials.username, os.getenv("USERNAME"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("PASSWORD"))
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


def _to_dataframe(file: UploadFile) -> pd.DataFrame:
    try:
        return pd.read_csv(file.file, sep=";", index_col="Unnamed: 0").reset_index(drop=True)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File could not be read.",
            headers={"WWW-Authenticate": "Basic"},
        )


def _validate_data(data: pd.DataFrame):
    missing_file_columns = set(COLUMNS) - set(data.columns)
    if missing_file_columns:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing columns: {','.join([column for column in sorted(missing_file_columns)])}.",
            headers={"WWW-Authenticate": "Basic"},
        )


def _send_to_lozuka(data: json):
    headers = {
        "X-Account": os.getenv("POA"),
        "Authorization": f"ApiKey {os.getenv('API_KEY')}",
        "Content-Type": "application/json",
        "accept": "*/*",
    }
    response = requests.post(os.getenv("LOZUKA_API_URL"), headers=headers, data=data)
    try:
        response.raise_for_status()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"message": f"Lozuka API request failed due to '{json.loads(response.content)}'", "status_code": response.status_code},
            headers={"WWW-Authenticate": "Basic"},
        )


COLUMNS = [
    "shop",
    "productNumber",
    "name",
    "description",
    "priceBrutto",
    "countryTax",
    "priceNet",
    "measureUnit",
    "measureQuantity",
    "basePriceUnit",
    "basePriceQuantity",
    "priceBase",
    "category",
    "image",
    "keywords",
    "stock",
    "ean",
    "brand",
]
route = Route(router=router, prefix="/integrate_products", tags=["Integrate Products"])
