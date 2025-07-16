# chatbot/chatbot.py

import streamlit as st
from utils.rag_engine import answer_query_from_policy

def run_chatbot_interface(uin):
    st.subheader(f"🧠 Ask questions about UIN {uin}")
    chat_history = st.session_state.get("chat_history", [])

    user_input = st.text_input("Ask a question about this policy:")

    if st.button("Ask"):
        if user_input:
            with st.spinner("Thinking..."):
                answer = answer_query_from_policy(uin, user_input)
                chat_history.append(("You", user_input))
                chat_history.append(("Bot", answer))
                st.session_state.chat_history = chat_history

    if chat_history:
        for speaker, msg in reversed(chat_history):
            st.markdown(f"**{speaker}:** {msg}")
