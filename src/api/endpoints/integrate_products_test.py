import json
import os
from typing import Dict
from dotenv import load_dotenv
import pandas as pd
import pytest
from fastapi import FastAPI
from requests.auth import HTTPBasicAuth
from starlette.testclient import TestClient
from .integrate_products import route, COLUMNS


load_dotenv("fixtures/test.env")
app = FastAPI()
app.include_router(**route)
test_client = TestClient(app)


def test_integrate_products_status_200(test_data):
    response = _post_test_csv_file(client=test_client, data=test_data)
    # TODO: check that Lozuka API is called with correct data
    assert response.status_code == 200
    assert json.loads(response.content)["detail"] == "Products added successfully"


@pytest.mark.vcr()
def test_integrate_products_authentification_status_401(test_data):
    response = _post_test_csv_file(client=test_client, data=test_data, auth=HTTPBasicAuth("falsche", "credentials"))
    assert response.status_code == 401
    assert json.loads(response.content)["detail"] == "Incorrect username or password"


@pytest.mark.vcr()
def test_integrate_products_missing_columns_status_422():
    response = _post_test_csv_file(client=test_client, data=pd.DataFrame({"wrong": ["data"]}))
    assert response.status_code == 422
    assert (
        json.loads(response.content)["detail"]
        == f"Missing columns: {','.join([column for column in sorted(COLUMNS)])}."
    )


@pytest.mark.vcr()
def test_integrate_products_lozuka_api_client_error_response_status_502(test_data):
    response = _post_test_csv_file(client=test_client, data=test_data)
    assert response.status_code == 502
    assert json.loads(response.content)["detail"] == {
        "message": "Lozuka API request failed due to '{'type': 'errors', 'data': [{'field': 'priceGross', 'message': "
        "'priceGross_is_required'}]}'",
        "status_code": 400,
    }


@pytest.mark.vcr()
def test_integrate_products_lozuka_api_authentification_error_response_status_502(test_data):
    response = _post_test_csv_file(client=test_client, data=test_data)
    assert response.status_code == 502
    assert json.loads(response.content)["detail"] == {
        "message": "Lozuka API request failed due to '{'message': 'Invalid credentials.'}'",
        "status_code": 401,
    }


def _post_test_csv_file(
    client: TestClient,
    data: pd.DataFrame,
    auth: HTTPBasicAuth = HTTPBasicAuth(os.getenv("USERNAME"), os.getenv("PASSWORD")),
):
    filename = "test.csv"
    data.to_csv(filename, sep=";")
    f = open(filename, "r")
    try:
        response = client.post("/integrate_products/", auth=auth, files={"file": f})
    finally:
        f.close()
        os.remove(filename)
    return response


@pytest.fixture
def test_data() -> pd.DataFrame:
    yield pd.read_csv("fixtures/products_testfile.csv", sep=";")


@pytest.fixture
def request_body() -> Dict:
    yield {
        "productNumber": "string",
        "active": True,
        "name": "string",
        "ean": "string",
        "countryTax": 0,
        "longDescription": "string",
        "availableFrom": "2022-01-01 00:00:00",
        "availableTo": "2022-01-02 12:00:00",
        "manufacturer": "string",
        "priceBase": 0,
        "baseMeasureUnit": "string",
        "baseMeasureQuantity": 0,
        "priceNet": 0,
        "priceGross": 0,
        "measureUnit": "string",
        "measureQuantity": 0,
        "leadDays": 0,
        "duration": "string",
        "description": "string",
        "stock": 0,
        "keywords": "string",
        "catalogs": [1, 3, 5],
        "categories": [1, 3, 5],
        "attributes": [{"name": "string", "value": "string"}],
        "images": "https://",
        "force_images_update": True,
    }
