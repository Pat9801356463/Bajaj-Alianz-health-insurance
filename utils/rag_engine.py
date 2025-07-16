# utils/rag_engine.py

from utils.doc_parser import extract_text_from_pdf
import google.generativeai as genai
import os

def init_gemini():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return genai.GenerativeModel("gemini-pro")

def answer_query_from_policy(uin, question):
    filepath = f"data/policies/{uin}.pdf"
    context = extract_text_from_pdf(filepath)[:30000]  # limit tokens

    model = init_gemini()
    prompt = f"""
You are a health insurance assistant. Use the following policy document content to answer user queries.

--- POLICY DOCUMENT CONTENT START ---
{context}
--- END ---

User question: {question}
"""

    response = model.generate_content(prompt)
    return response.text.strip()
