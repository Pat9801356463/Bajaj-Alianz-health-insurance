# app.py

import streamlit as st
import pandas as pd
from utils.policy_loader import load_policy_data
from utils.policy_filter import filter_policies
from chatbot.chatbot import run_chatbot_interface

st.set_page_config(page_title="🩺 Bajaj Allianz Policy Recommender", layout="centered")

st.title("🏥 Bajaj Allianz Health Insurance Finder")

# Load and clean Data
df = load_policy_data()
df.columns = df.columns.str.strip()

# Input Form
with st.form("filter_form"):
    st.subheader("🔍 Enter Your Details")
    age = st.text_input("Enter your age", placeholder="e.g. 35")
    product_type = st.selectbox("Type of Product", sorted(df["Type Of Product"].dropna().unique()))
    identity = st.selectbox("Identity", sorted(df["Identity"].dropna().unique()))
    disease_type = st.selectbox("Disease Type", sorted(df["Disease Type"].dropna().unique()))
    coverage = st.text_input("Enter coverage (e.g., 10L, 1Cr, 500000)", placeholder="10L")

    submitted = st.form_submit_button("Show Matching Policies")

if submitted:
    try:
        result_df = filter_policies(df, age, product_type, identity, disease_type, coverage)

        if result_df.empty:
            st.warning("No matching policies found.")
        else:
            st.success(f"Found {len(result_df)} matching policy(ies).")

            # Show result table (without predicted premium)
            st.dataframe(result_df[[
                "UIN", "Product Name", "Type Of Product", "Age", "Identity", 
                "Disease Type", "Net Coverage Amount (Sum Insured)", "Documents"
            ]])

            # Chatbot for selected policy
            selected_uin = st.selectbox("📄 Select a Policy UIN to Chat With:", result_df["UIN"].unique())
            if st.button("Start Chatbot"):
                run_chatbot_interface(selected_uin)

    except Exception as e:
        st.error(f"❌ Error: {e}")
