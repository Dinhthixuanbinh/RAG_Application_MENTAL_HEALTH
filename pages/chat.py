# pages/chat.py
import streamlit as st
from loguru import logger
from src.conversation_engine import initialize_chatbox, load_chat_store
from src.global_settings import SCORES_FILE, CONVERSATION_FILE
import os
import json

def get_session_info():
    """Retrieves or initializes session information for the chat."""
    if "username" not in st.session_state:
        st.error("Please log in first.")
        return None, None
    
    username = st.session_state.username
    user_info = st.session_state.user_info
    return username, user_info

def handle_user_input(agent, prompt):
    """Handles user input and generates a response from the agent."""
    with st.spinner("Generating response..."):
        response = agent.chat(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.response})
        st.session_state.messages.append({"role": "assistant", "content": response.tool_calls[0].tool_call_data.kwargs["score"]}) # this need to be verify with conversation engine

def main():
    """Main function for the Streamlit chat page."""
    username, user_info = get_session_info()
    if not username:
        return

    st.title(f"🧠 Chat with the Mental Health Assistant")
    st.markdown(f"**Logged in as**: `{username}`")

    # Load chat history from file
    chat_store = load_chat_store()
    agent = initialize_chatbox(chat_store=chat_store, container=None, username=username, user_info=user_info)
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Restore past messages from chat store
        if username in chat_store.chat_dicts:
            for message in chat_store.chat_dicts[username]:
                st.session_state.messages.append({"role": message.role, "content": message.content})

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    prompt = st.chat_input("Ask a question about mental health...")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        handle_user_input(agent, prompt)

if __name__ == "__main__":
    logger.info("Starting chat.py")
    main()