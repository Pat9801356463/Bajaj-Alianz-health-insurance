# utils/rag_engine.py

import os
import google.generativeai as genai
from utils.doc_parser import extract_text_from_pdf

# Configure Gemini once
def init_gemini():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return genai.GenerativeModel(
        model_name="models/gemini-1.5-flash-latest",  # use latest flash model
        system_instruction="You are a helpful assistant trained to answer questions using health insurance policy documents."
    )

# Main RAG function
def answer_query_from_file(file_path, question):
    try:
        # Extract context from PDF file
        context = extract_text_from_pdf(file_path)
        if not context.strip():
            return "The policy document is empty or unreadable."

        context = context[:30000]  # limit for token safety

        model = init_gemini()

        # Chat-style input
        response = model.generate_content([
            {"role": "user", "parts": [
                f"Based on the following insurance policy document, answer this question:\n\n"
                f"--- DOCUMENT START ---\n{context}\n--- DOCUMENT END ---\n\n"
                f"Question: {question}"
            ]}
        ])

        return response.text.strip()
    except Exception as e:
        return f"Error generating answer: {e}"
