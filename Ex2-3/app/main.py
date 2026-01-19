import joblib
import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, make_asgi_app

model = None

# -------------------- Readiness ----------------------- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application's lifespan by loading the Iris model into the module-level `model` variable at startup.
    
    Loads the model from "models/iris_model.joblib" and assigns it to the global `model` before yielding control to the application.
    """
    global model
    model = joblib.load("models/iris_model.joblib")
    yield
app = FastAPI(lifespan=lifespan)

@app.get("/ready")
def ready():
    """
    Report service readiness based on whether the ML model has been loaded.
    
    Returns:
        If the global model is loaded, `{"status": "ready"}`; otherwise an HTTP 503 JSONResponse with `{"status": "not_ready"}`.
    """
    if model is not None:
        return {"status": "ready"}
    return JSONResponse(status_code=503, content={"status": "not_ready"})

# -------------------- Prometheus ---------------------- #
PREDICTION_LATENCY = Histogram(
    "prediction_latency_seconds",
    "Latency of predictions in seconds"
)
PREDICTION_COUNT = Counter(
    "prediction_count",
    "Total count of predictions",
    ["status"]
)
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# -------------------- Inference ----------------------- #
class IrisInput(BaseModel):
    sepalLength: float
    sepalWidth: float
    petalLength: float
    petalWidth: float

@app.post("/predict")
def predict(data: IrisInput):
    """
    Predict the iris species from sepal and petal measurements.
    
    Parameters:
        data (IrisInput): Measurements with fields `sepalLength`, `sepalWidth`, `petalLength`, and `petalWidth`.
    
    Returns:
        dict: {"species": <predicted species>} where <predicted species> is the model's predicted class label.
    """
    with PREDICTION_LATENCY.time():
        try:
            features = pd.DataFrame([[
                data.sepalLength,
                data.sepalWidth,
                data.petalLength,
                data.petalWidth
            ]], columns=model.feature_names_in_)

            prediction = model.predict(features)[0]
            PREDICTION_COUNT.labels(status="success").inc()
            return {"species": prediction}
        except Exception:
            PREDICTION_COUNT.labels(status="failure").inc()
            raise