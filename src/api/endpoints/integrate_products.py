import json
import secrets
import os
from typing import Dict, List

import pandas as pd
import requests

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from dotenv import load_dotenv
from src.types import Route

router = APIRouter()
security = HTTPBasic()
load_dotenv("credentials.env")


@router.post("/")
def integrate_products(file: UploadFile, credentials: HTTPBasicCredentials = Depends(security)):
    _validate_credentials(credentials)
    data = _to_dataframe(file)
    data = _validate_data(data)
    data = _set_types(data)
    data = _fill_nan_values(data)
    data = _structure_data(data)
    failed_requests = _send_data(data)
    return {
        "detail": {
            "failed": failed_requests,
        }
    }


def _validate_credentials(credentials: HTTPBasicCredentials):
    correct_username = secrets.compare_digest(credentials.username, os.getenv("ACCOUNT"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("PASSWORD"))
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


def _to_dataframe(file: UploadFile) -> pd.DataFrame:
    try:
        return pd.read_csv(file.file, sep=";").reset_index(drop=True)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File could not be read.",
            headers={"WWW-Authenticate": "Basic"},
        )


def _set_types(data: pd.DataFrame) -> pd.DataFrame:
    for column, attribute_type in COLUMNS.items():
        if column == "shop":
            continue
        data[column] = data[column].astype(attribute_type)
    return data


def _fill_nan_values(data: pd.DataFrame) -> pd.DataFrame:
    for col in data:
        dt = data[col].dtype
        if dt == int or dt == float:
            data[col].fillna(0, inplace=True)
        else:
            data[col].fillna("", inplace=True)
    return data


def _validate_data(data: pd.DataFrame) -> pd.DataFrame:
    missing_file_columns = set(COLUMNS.keys()) - set(data.columns)
    if missing_file_columns:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing columns: {','.join([column for column in sorted(missing_file_columns)])}.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return data


def _structure_data(data: pd.DataFrame) -> Dict[str, List[Dict]]:
    shops = data["shop"].unique()
    structured_data = {}
    for shop in shops:
        structured_data[shop] = [
            product for key, product in data[data["shop"] == shop].drop(columns=["shop"]).to_dict("index").items()
        ]
    return structured_data


def _send_data(data: Dict[str, List[Dict]]) -> Dict:
    failed_requests = {}
    for shop_name, shop_products in data.items():
        failed_requests[shop_name] = _send_shop_products(shop=shop_name, products=shop_products)
    return failed_requests


def _send_shop_products(shop: str, products: List[Dict]) -> Dict[str, Dict]:
    failed_requests = {}
    for product in products:
        response = _send_product(shop=shop, data=product)
        try:
            response.raise_for_status()
        except Exception:
            failed_requests[product["productNumber"]] = {
                "content": json.loads(response.content),
                "status_code": response.status_code,
            }
    return failed_requests


def _send_product(shop: str, data: Dict):
    shop = shop.upper().replace(" ", "")
    headers = {
        "X-Account": os.getenv(f"{shop}_POA"),
        "Authorization": f"ApiKey {os.getenv(f'{shop}_API_KEY')}",
        "Content-Type": "application/json",
        "accept": "*/*",
    }
    return requests.post(os.getenv("LOZUKA_API_URL"), headers=headers, json=data)


COLUMNS = {
    "shop": str,
    "productNumber": str,
    "name": str,
    "description": str,
    "priceGross": float,
    "countryTax": int,
    "priceNet": float,
    "measureUnit": str,
    "measureQuantity": float,
    "baseMeasureUnit": str,
    "baseMeasureQuantity": float,
    "categories": str,
    "images": str,
    "keywords": str,
    "stock": float,
    "ean": str,
    "active": bool,
    "force_images_update": bool,
}
route = Route(router=router, prefix="/integrate_products", tags=["Integrate Products"])
