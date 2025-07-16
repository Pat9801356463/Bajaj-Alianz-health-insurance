# utils/policy_filter.py

import pandas as pd
import re

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
        return None  # for "Varies" or unknown text

def filter_policies(df, age_str, product_type, identity, disease_type, coverage_str):
    try:
        age = float(age_str)
    except ValueError:
        raise ValueError("Invalid age input.")

    coverage = parse_coverage(coverage_str)

    results = []

    for _, row in df.iterrows():
        # --- AGE check
        min_age, max_age = parse_age_range(row["Age"])
        if min_age is not None and (age < min_age or age > max_age):
            continue

        # --- PRODUCT TYPE check
        if str(row["Type of product"]).strip() != product_type.strip():
            continue

        # --- DISEASE TYPE strict match
        if str(row["Disease Type"]).strip() != disease_type.strip():
            continue

        # --- IDENTITY check
        row_identity = str(row["Identity"]).strip()
        if row_identity != identity and row_identity != "All":
            continue

        # --- COVERAGE match with ±10% tolerance
        row_coverage = parse_coverage(row["Coverage"])
        if row_coverage is not None and coverage is not None:
            lower = coverage * 0.9
            upper = coverage * 1.1
            if not (lower <= row_coverage <= upper):
                continue
        elif coverage is not None and row_coverage is None:
            continue  # skip "varies" when user input is numeric

        # all filters passed
        results.append(row)

    return pd.DataFrame(results)
