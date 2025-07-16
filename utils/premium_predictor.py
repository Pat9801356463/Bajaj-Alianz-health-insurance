# utils/premium_predictor.py

import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

# Train once and reuse
model = None

def train_premium_model(csv_path="data/premium_model.csv"):
    global model

    df = pd.read_csv(csv_path)
    df = df.dropna()

    # Convert coverage to ₹ if needed
    def parse_cov(x):
        x = str(x).strip().lower()
        if 'cr' in x:
            return float(x.replace("cr", "").strip()) * 1e7
        elif 'lac' in x:
            return float(x.replace("lac", "").strip()) * 1e5
        return float(x)

    df["Coverage INR"] = df["Coverage"].apply(parse_cov)
    df["Price"] = (df["Starting Price"] + df["End Price"]) / 2

    X = df[["Coverage INR"]]
    y = df["Price"]

    model = LinearRegression()
    model.fit(X, y)

def predict_premium(coverage_input):
    if model is None:
        train_premium_model()

    # Parse input coverage
    val = str(coverage_input).strip().lower()
    if 'cr' in val:
        cov = float(val.replace("cr", "")) * 1e7
    elif 'lac' in val:
        cov = float(val.replace("lac", "")) * 1e5
    else:
        cov = float(val)

    prediction = model.predict(np.array([[cov]]))[0]
    return round(prediction, 2)
