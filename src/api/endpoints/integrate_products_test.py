import json
import os

from fastapi import FastAPI
from starlette.testclient import TestClient
from src.types import Route
from .integrate_products import route


def test_integrate_products_authentification_access_granted():
    os.environ["LOGIN"] = "test"
    os.environ["PASSWORD"] = "testpw"
    test_data = {"test": "test"}

    test_client = create_test_client(route)
    res = test_client.post("/transform/", headers={"Authorization": "Basic dGVzdDp0ZXN0cHc="}, json=test_data)
    assert json.loads(res.content)["products"] == test_data


def test_integrate_products_authentification_access_denied():
    test_client = create_test_client(route)
    res = test_client.post("/transform/", headers={"Authorization": "Basic Blödsinn"}, data={"test": "test"})
    assert json.loads(res.content)["detail"] == "Invalid authentication credentials"


def test_integrate_products_rejects_faulty_data():
    assert True


def test_integrate_products_returns_success_message_on_success():
    assert True


def create_test_client(route: Route):
    app = FastAPI()
    app.include_router(**route)
    return TestClient(app)
