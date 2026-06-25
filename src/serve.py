from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import joblib
import os

app = FastAPI()

S3_BUCKET = os.environ["CLOUD_BUCKET"]
S3_MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = os.path.expanduser("~/models/model.pkl")


def download_model():
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    s3_client = boto3.client("s3")
    s3_client.download_file(S3_BUCKET, S3_MODEL_KEY, MODEL_PATH)
    print(f"Downloaded s3://{S3_BUCKET}/{S3_MODEL_KEY} to {MODEL_PATH}.")


try:
    download_model()
    model = joblib.load(MODEL_PATH)
except Exception as exc:
    print(f"Model is not ready yet: {exc}")
    model = None


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded yet")

    if len(req.features) != 12:
        raise HTTPException(
            status_code=400,
            detail="Expected 12 features (wine quality)",
        )

    prediction = int(model.predict([req.features])[0])
    labels = {0: "thap", 1: "trung_binh", 2: "cao"}
    return {"prediction": prediction, "label": labels[prediction]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
