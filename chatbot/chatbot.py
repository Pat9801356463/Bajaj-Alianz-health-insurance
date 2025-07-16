# chatbot/chatbot.py

import streamlit as st
from utils.rag_engine import answer_query_from_file
from utils.policy_loader import load_policy_data

def run_chatbot_interface(selected_uin):
    st.subheader(f"🧠 Ask questions about UIN {selected_uin}")
    df = load_policy_data()

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
