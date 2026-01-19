import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

# --------------------- Global --------------------------------- #
GOLDEN_PATH = Path("tests/golden_data.json")
MODEL_PATH = Path("models/iris_model.joblib")

with open(GOLDEN_PATH) as file:
    golden = json.load(file)
    inference = golden["inference"]
    ENDPOINT = inference["endpoint"]
    PAYLOAD = inference["payload"]
    EXPECTED_KEY = inference["key"]
    EXPECTED_VALUE = inference["expected"]

# --------------------- Fix por readiness --------------------- #
# Se requiere para cargar el modelo tras agregar el lifespan para
# el readiness de Prometheus cuando se usa en pytest
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# --------------------- UT APP ------------------------------- #
def test_modelExist():
    assert MODEL_PATH.exists()

def test_predictReturns(client):
    response = client.post(ENDPOINT, json=PAYLOAD)
    assert response.status_code == 200
    assert EXPECTED_KEY in response.json()

def test_predictExpectedSpecies(client):
    response = client.post(ENDPOINT, json=PAYLOAD)
    result = response.json()[EXPECTED_KEY]
    assert result == EXPECTED_VALUE
