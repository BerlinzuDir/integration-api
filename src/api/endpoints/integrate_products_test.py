import json
import os
import pdb
from typing import Dict

import pandas as pd
import pytest
from fastapi import FastAPI, UploadFile
from requests.auth import HTTPBasicAuth
from starlette.testclient import TestClient
from src.types import Route
from .integrate_products import route

USERNAME = 'test'
PASSWORD = "testpw"


def test_integrate_products_status_200(test_data):
    test_client = _setup()
    res = _post_test_csv_file(client=test_client, data=test_data)
    assert res.status_code == 200


def test_integrate_products_authentification_status_401(test_data):
    test_client = _setup()
    response = _post_test_csv_file(client=test_client, data=test_data, auth=HTTPBasicAuth("falsche", "credentials"))
    assert response.status_code == 401
    assert json.loads(response.content)["detail"] == "Incorrect username or password"


def test_integrate_products_faulty_data_status_422():
    test_client = _setup()
    response = _post_test_csv_file(client=test_client, data=pd.DataFrame({'wrong': ["data"]}))
    assert response.status_code == 422
    assert json.loads(response.content)["detail"] == "Invalid file structure"


def _setup():
    _set_env_variables(username=USERNAME, password=PASSWORD)
    return _create_test_client(route)


def _post_test_csv_file(
        client: TestClient,
        data: pd.DataFrame,
        auth: HTTPBasicAuth = HTTPBasicAuth(USERNAME, PASSWORD),
):
    filename = "test.csv"
    data.to_csv(filename)
    f = open(filename, 'r')
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


@pytest.fixture
def test_data() -> pd.DataFrame:
    yield pd.read_csv("fixtures/products_testfile.csv", delimiter='\t')

