import pandas as pd
import re

# ----------------------
# POLICY FILTER LOGIC ONLY
# ----------------------

def parse_age_range(age_range):
    match = re.match(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", str(age_range))
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

def parse_coverage(val):
    val = str(val).strip().lower().replace(" ", "")
    if 'varies' in val:
        return None
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
    if coverage is None:
        return pd.DataFrame([])  # Invalid or unsupported coverage input

    results = []

    for _, row in df.iterrows():
        # Age check
        min_age, max_age = parse_age_range(row["Age"])
        if min_age is not None and (age < min_age or age > max_age):
            continue

        # Product type
        if str(row["Type Of Product"]).strip() != product_type.strip():
            continue

        # Disease type
        if str(row["Disease Type"]).strip() != disease_type.strip():
            continue

        # Identity
        row_identity = str(row["Identity"]).strip()
        if row_identity != identity and row_identity != "All":
            continue

        # Coverage match
        raw_cov = str(row["Net Coverage Amount (Sum Insured)"]).lower()
        if "varies" in raw_cov:
            continue

        row_coverage = parse_coverage(raw_cov)
        if row_coverage is None:
            continue

        lower = coverage * 0.9
        upper = coverage * 1.1
        if not (lower <= row_coverage <= upper):
            continue

        # Add matched row
        results.append(row.to_dict())

    return pd.DataFrame(results)
