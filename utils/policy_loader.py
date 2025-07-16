# utils/policy_loader.py

import pandas as pd

def load_policy_data():
    return pd.read_csv("Data/fp.csv")
