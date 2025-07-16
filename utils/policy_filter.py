import pandas as pd
import re
import numpy as np
from sklearn.linear_model import LinearRegression

# ----------------------
# PREMIUM MODEL SETUP
# ----------------------
premium_model = None

def train_premium_model(csv_path="Data/premium_model.csv"):
    global premium_model

    df = pd.read_csv(csv_path).dropna()

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

    premium_model = LinearRegression()
    premium_model.fit(X, y)

def predict_premium(coverage_input):
    if premium_model is None:
        train_premium_model()

    val = str(coverage_input).strip().lower().replace(" ", "")
    if 'cr' in val:
        cov = float(val.replace("cr", "")) * 1e7
    elif 'lac' in val:
        cov = float(val.replace("lac", "")) * 1e5
    elif 'l' in val:
        cov = float(val.replace("l", "")) * 1e5
    else:
        cov = float(val)

    prediction = premium_model.predict(np.array([[cov]]))[0]
    return round(prediction, 2)

# ----------------------
# POLICY FILTER LOGIC
# ----------------------

def parse_age_range(age_range):
    match = re.match(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", str(age_range))
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

def parse_coverage(val):
    val = str(val).strip().lower().replace(" ", "")
    if 'cr' in val:
        return float(re.sub(r'[^\d.]', '', val)) * 1e7
    elif 'lac' in val or 'lakh' in val or 'l' in val:
        return float(re.sub(r'[^\d.]', '', val)) * 1e5
    elif val.replace('.', '', 1).isdigit():
        return float(val)
    else:
        return None

def filter_policies(df, age_str, product_type, identity, disease_type, coverage_str):
    df.columns = df.columns.str.strip()

    try:
        age = float(age_str)
    except ValueError:
        raise ValueError("Invalid age input.")

    coverage = parse_coverage(coverage_str)
    results = []

    for _, row in df.iterrows():
        min_age, max_age = parse_age_range(row["Age"])
        if min_age is not None and (age < min_age or age > max_age):
            continue

        if str(row["Type Of Product"]).strip() != product_type.strip():
            continue

        if str(row["Disease Type"]).strip() != disease_type.strip():
            continue

        row_identity = str(row["Identity"]).strip()
        if row_identity != identity and row_identity != "All":
            continue

        row_coverage = parse_coverage(row["Net Coverage Amount (Sum Insured)"])
        if row_coverage is not None and coverage is not None:
            lower = coverage * 0.9
            upper = coverage * 1.1
            if not (lower <= row_coverage <= upper):
                continue
        elif coverage is not None and row_coverage is None:
            pass
        else:
            continue

        row_dict = row.to_dict()
        row_dict["Predicted Premium"] = f"₹{predict_premium(coverage_str):,.2f}/year"
        results.append(row_dict)

    return pd.DataFrame(results)
