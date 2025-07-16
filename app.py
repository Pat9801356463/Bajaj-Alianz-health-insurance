# app.py

import streamlit as st
import pandas as pd
import os
from utils.policy_loader import load_policy_data
from utils.policy_filter import filter_policies
from utils.rag_engine import answer_query_from_file

st.set_page_config(page_title="🩺 Bajaj Allianz Policy Recommender", layout="centered")

st.title("🏥 Bajaj Allianz Health Insurance Finder")

# Load and clean Data
df = load_policy_data()
df.columns = df.columns.str.strip()

# -------------------------------
# Chatbot Interface (from chatbot.py)
# -------------------------------
def run_chatbot_interface(selected_uin):
    st.subheader(f"🧠 Ask questions about UIN {selected_uin}")
    df = load_policy_data()
    df.columns = df.columns.str.strip()

    # Locate the document path for this UIN
    try:
        doc_path = df[df["UIN"] == selected_uin]["Document address"].values[0]
        if not doc_path or not os.path.isfile(doc_path):
            st.error(f"Document not found at path: {doc_path}")
            return
    except Exception as e:
        st.error(f"Unable to locate document path: {e}")
        return

    chat_history = st.session_state.get("chat_history", [])

    user_input = st.text_input("Ask a question about this policy:")

    if st.button("Ask"):
        if user_input:
            with st.spinner("Thinking..."):
                answer = answer_query_from_file(doc_path, user_input)
                chat_history.append(("You", user_input))
                chat_history.append(("Bot", answer))
                st.session_state.chat_history = chat_history

    if chat_history:
        for speaker, msg in reversed(chat_history):
            st.markdown(f"**{speaker}:** {msg}")

# -------------------------------
# Filter Form UI
# -------------------------------
with st.form("filter_form"):
    st.subheader("🔍 Enter Your Details")
    age = st.text_input("Enter your age", placeholder="e.g. 35")
    product_type = st.selectbox("Type of Product", sorted(df["Type Of Product"].dropna().unique()))
    identity = st.selectbox("Identity", sorted(df["Identity"].dropna().unique()))
    disease_type = st.selectbox("Disease Type", sorted(df["Disease Type"].dropna().unique()))
    coverage = st.text_input("Enter coverage (e.g., 10L, 1Cr, 500000)", placeholder="10L")

    submitted = st.form_submit_button("Show Matching Policies")

# -------------------------------
# Run Filter & Display Results
# -------------------------------
if submitted:
    try:
        result_df = filter_policies(df, age, product_type, identity, disease_type, coverage)

        if result_df.empty:
            st.warning("No matching policies found.")
        else:
            st.success(f"Found {len(result_df)} matching policy(ies).")

            st.dataframe(result_df[[
                "UIN", "Product Name", "Type Of Product", "Age", "Identity", 
                "Disease Type", "Net Coverage Amount (Sum Insured)", "Documents"
            ]])

            selected_uin = st.selectbox("📄 Select a Policy UIN to Chat With:", result_df["UIN"].unique())
            if st.button("Start Chatbot"):
                run_chatbot_interface(selected_uin)

    except Exception as e:
        st.error(f"❌ Error: {e}")
