import json
import os
from typing import Dict

import pandas as pd
import pytest
import responses
from fastapi import FastAPI
from requests.auth import HTTPBasicAuth
from starlette.testclient import TestClient
from src.types import Route
from .integrate_products import route, COLUMNS

USERNAME = "test"
PASSWORD = "testpw"
LOZUKA_API_URL = "https://test_api.com/"


@responses.activate
def test_integrate_products_status_200(test_data, request_body):
    test_client = _setup()
    _mock_product_import_endpoint()

    response = _post_test_csv_file(client=test_client, data=test_data)
    # TODO: check that Lozuka API is called with correct data
    assert len(responses.calls) == 1
    assert responses.calls[0].request.body == request_body
    assert response.status_code == 200
    assert json.loads(response.content)["detail"] == "Products added successfully"


def test_integrate_products_authentification_status_401(test_data):
    test_client = _setup()
    response = _post_test_csv_file(client=test_client, data=test_data, auth=HTTPBasicAuth("falsche", "credentials"))
    assert response.status_code == 401
    assert json.loads(response.content)["detail"] == "Incorrect username or password"


def test_integrate_products_missing_columns_status_422():
    test_client = _setup()
    response = _post_test_csv_file(client=test_client, data=pd.DataFrame({"wrong": ["data"]}))
    assert response.status_code == 422
    assert (
        json.loads(response.content)["detail"]
        == f"Missing columns: {','.join([column for column in sorted(COLUMNS)])}."
    )


def test_integrate_products_lozuka_api_error_response_status_502():
    test_client = _setup()
    response = _post_test_csv_file(client=test_client, data=pd.DataFrame({"wrong": ["data"]}))
    assert response.status_code == 502
    assert json.loads(response.content)["detail"] == {
        "message": "Lozuka API request failed due to 'Access denied'",
        "status_code": 401,
    }


def _setup():
    _set_env_variables(username=USERNAME, password=PASSWORD, lozuka_api_url=LOZUKA_API_URL)
    return _create_test_client(route)


def _post_test_csv_file(
    client: TestClient,
    data: pd.DataFrame,
    auth: HTTPBasicAuth = HTTPBasicAuth(USERNAME, PASSWORD),
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


def _set_env_variables(**kwargs):
    for key, value in kwargs.items():
        os.environ[key.upper()] = value


def _create_test_client(route: Route):
    app = FastAPI()
    app.include_router(**route)
    return TestClient(app)


def _mock_product_import_endpoint() -> None:
    responses.add(
        responses.POST,
        os.getenv("LOZUKA_API_URL"),
        match_querystring=True,
        body="",
        status=200,
    )


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
