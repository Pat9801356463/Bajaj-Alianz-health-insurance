import streamlit as st
import pandas as pd
import os
import re
import PyPDF2
import google.generativeai as genai
from utils.policy_filter import filter_policies
from utils.policy_loader import load_policy_data

# -------------------------
# Gemini Chatbot Logic
# -------------------------

def extract_text_from_pdf(file_path):
    try:
        reader = PyPDF2.PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text[:30000]
    except Exception as e:
        return f"❌ Failed to read PDF: {e}"

def init_gemini():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return genai.GenerativeModel("gemini-1.5-flash")

def answer_query_from_file(file_path, question):
    context = extract_text_from_pdf(file_path)
    model = init_gemini()
    prompt = f"""
You are a health insurance assistant. Use the following policy document content to answer the user's question.

--- POLICY DOCUMENT START ---
{context}
--- END OF POLICY ---

User question: {question}
"""
    response = model.generate_content(prompt)
    return response.text.strip()

def run_chatbot_interface(selected_uin):
    st.subheader(f"🧠 Ask questions about UIN {selected_uin}")
    df = load_policy_data()
    df.columns = df.columns.str.strip()

    try:
        doc_path = df[df["UIN"] == selected_uin]["Documents"].values[0]
        if not doc_path or not os.path.isfile(doc_path):
            st.error(f"📂 Document not found: {doc_path}")
            return
    except Exception as e:
        st.error(f"Error locating document path: {e}")
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
        st.markdown("### 💬 Chat History")
        for speaker, msg in reversed(chat_history):
            st.markdown(f"**{speaker}:** {msg}")

# -------------------------
# Streamlit App UI
# -------------------------

st.set_page_config(page_title="🩺 Bajaj Allianz Policy Recommender", layout="centered")
st.title("🏥 Bajaj Allianz Health Insurance Finder")

# Load data
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

# Handle form submit
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

            if "chatbot_active" not in st.session_state:
                st.session_state.chatbot_active = False

            if st.button("Start Chatbot"):
                st.session_state.chatbot_active = True
                st.session_state.selected_uin = selected_uin
                st.session_state.chat_history = []

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ✅ THIS IS NOW OUTSIDE THE TRY BLOCK
if st.session_state.get("chatbot_active", False):
    run_chatbot_interface(st.session_state.get("selected_uin"))
