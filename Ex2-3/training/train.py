import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

data = pd.read_csv("data/Iris.csv")

X = data[["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"]]
y = data["Species"]

model = RandomForestClassifier()
model.fit(X, y)

joblib.dump(model, "models/iris_model.joblib")

print(f"Accuracy: {model.score(X, y)}")
