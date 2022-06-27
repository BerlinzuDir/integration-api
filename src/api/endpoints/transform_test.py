import json

from fastapi import FastAPI
from starlette.testclient import TestClient
from src.types import Route
from .transform import route


def test_transform_authentification_access_granted():
    test_client = create_test_client(route)
    res = test_client.post("/api/transform/", json=json.dumps({"test":"test"}))
    import pdb;pdb.set_trace()
    assert False


def test_transform_authentification_access_denied():
    assert False


def test_transform_rejects_faulty_data():
    assert True


def test_transform_returns_success_message_on_success():
    assert True


def create_test_client(route: Route):
    app = FastAPI()
    app.include_router(**route)
    return TestClient(app)
