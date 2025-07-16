# utils/policy_filter.py

import pandas as pd
import re

def parse_age_range(age_range):
    match = re.match(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", str(age_range))
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

def parse_coverage(val):
    val = str(val).strip().lower()
    if 'cr' in val:
        return float(re.sub(r'[^\d.]', '', val)) * 1e7
    elif 'lac' in val or 'lakh' in val:
        return float(re.sub(r'[^\d.]', '', val)) * 1e5
    elif val.isnumeric():
        return float(val)
    else:
        return None  # for "varies" or unknown

def filter_policies(df, age_str, product_type, identity, disease_type, coverage_str):
    age = float(age_str)
    coverage = parse_coverage(coverage_str)

    results = []

    for _, row in df.iterrows():
        min_age, max_age = parse_age_range(row["Age"])
        if min_age is not None and (age < min_age or age > max_age):
            continue

        if str(row["Type of product"]).strip() != product_type.strip():
            continue

        if str(row["Disease Type"]).strip() != disease_type.strip():
            continue

        row_identity = str(row["Identity"]).strip()
        if row_identity != identity and row_identity != "All":
            continue

        row_coverage = parse_coverage(row["Coverage"])
        if row_coverage and coverage and row_coverage < coverage:
            continue

        results.append(row)

    return pd.DataFrame(results)
