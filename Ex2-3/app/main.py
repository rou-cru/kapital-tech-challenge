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
    global model
    model = joblib.load("models/iris_model.joblib")
    yield
app = FastAPI(lifespan=lifespan)

@app.get("/ready")
def ready():
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
