import json
import os
from dotenv import load_dotenv
import pandas as pd
import pytest
from fastapi import FastAPI
from requests.auth import HTTPBasicAuth
from starlette.testclient import TestClient

from .integrate_products import route, COLUMNS, _set_categories_as_list

load_dotenv("fixtures/test.env")
app = FastAPI()
app.include_router(**route)
test_client = TestClient(app)


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["Authorization", "X-Account"]}


@pytest.mark.vcr()
def test_integrate_products_status_200(test_data):
    response = _post_test_csv_file(client=test_client, data=test_data)
    # TODO: check that Lozuka API is called with correct data
    assert response.status_code == 200
    assert json.loads(response.content) == {"detail": {"failed": {"Almahaba Supermarkt": {}, "Malandra": {}}}}


@pytest.mark.vcr()
def test_integrate_products_lozuka_api_authentification_error_response_status_200(test_data):
    os.environ["ALMAHABASUPERMARKT_API_KEY"] = "1234"
    os.environ["ALMAHABASUPERMARKT_POA"] = "1234"
    response = _post_test_csv_file(client=test_client, data=test_data)
    assert response.status_code == 200
    assert json.loads(response.content) == {
        "detail": {
            "failed": {
                "Almahaba Supermarkt": {
                    "1": {"content": {"message": "Invalid credentials."}, "status_code": 401},
                    "2": {"content": {"message": "Invalid credentials."}, "status_code": 401},
                    "3": {"content": {"message": "Invalid credentials."}, "status_code": 401},
                    "4": {"content": {"message": "Invalid credentials."}, "status_code": 401},
                    "5": {"content": {"message": "Invalid credentials."}, "status_code": 401},
                    "6": {"content": {"message": "Invalid credentials."}, "status_code": 401},
                    "7": {"content": {"message": "Invalid credentials."}, "status_code": 401},
                },
                "Malandra": {},
            }
        }
    }


def test_integrate_products_authentification_status_401(test_data):
    response = _post_test_csv_file(client=test_client, data=test_data, auth=HTTPBasicAuth("falsche", "credentials"))
    assert response.status_code == 401
    assert json.loads(response.content)["detail"] == "Incorrect username or password"


def test_integrate_products_missing_columns_status_422():
    response = _post_test_csv_file(client=test_client, data=pd.DataFrame({"wrong": ["data"]}))
    assert response.status_code == 422
    assert (
        json.loads(response.content)["detail"]
        == f"Missing columns: {','.join([column for column in sorted(COLUMNS.keys())])}."
    )


def _post_test_csv_file(
    client: TestClient,
    data: pd.DataFrame,
    auth: HTTPBasicAuth = HTTPBasicAuth(os.getenv("ACCOUNT"), os.getenv("PASSWORD")),
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


def test_set_category_as_list_converts_category_column_to_list():
    data = pd.DataFrame({"categories": ["1", "2", "3"]})
    data = _set_categories_as_list(data)
    assert all([a == b for a, b in zip(data.categories.values, [["1"], ["2"], ["3"]])])

@pytest.fixture
def test_data() -> pd.DataFrame:
    yield pd.read_csv("fixtures/products_testfile.csv", sep=";")
