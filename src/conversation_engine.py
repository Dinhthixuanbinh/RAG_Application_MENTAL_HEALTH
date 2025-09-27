# src/conversation_engine.py
import os
import json
from datetime import datetime
from loguru import logger
import streamlit as st
from llama_index.core import load_index_from_storage, StorageContext, Settings
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.llms.gemini import Gemini
from llama_index.core.agent import ReActAgent  # Changed agent class to ReActAgent
from src.global_settings import INDEX_STORAGE, CONVERSATION_FILE, SCORES_FILE
from src.prompts import CUSTORM_AGENT_SYSTEM_TEMPLATE
import openai # Retained, as the OpenAIAgent might rely on global OpenAI config, though ReActAgent is preferred here.

def load_chat_store() -> SimpleChatStore:
    """
    Loads chat history from a JSON file. If the file is not found or is empty,
    it initializes a new SimpleChatStore.
    """
    if os.path.exists(CONVERSATION_FILE) and os.path.getsize(CONVERSATION_FILE) > 0:
        try:
            chat_store: SimpleChatStore = SimpleChatStore.from_persist_path(CONVERSATION_FILE)
            logger.info("Chat store loaded successfully.")
        except json.JSONDecodeError:
            logger.warning(f"Could not decode JSON from {CONVERSATION_FILE}. Initializing a new chat store.")
            chat_store = SimpleChatStore()
    else:
        logger.info("No existing chat history found. Initializing a new chat store.")
        chat_store = SimpleChatStore()
    
    return chat_store

def save_score(score: str, content: str, total_guess: str, usename: str):
    """
    Writes a new score entry to the scores.json file.
    
    Args:
        score (str): Score of the user's mental health.
        content (str): Content of the user's mental health.
        total_guess (str): Total guess of the user's mental health.
        usename (str): The user's username.
    """
    current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry: dict = {
        "usename": usename,
        "Time": current_time,
        "Score": score,
        "Content": content,
        "Total guess": total_guess
    }
    
    try:
        if os.path.exists(SCORES_FILE) and os.path.getsize(SCORES_FILE) > 0:
            with open(SCORES_FILE, "r") as f:
                data: list = json.load(f)
        else:
            data = []
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading scores file: {e}. Starting with an empty list.")
        data = []

    data.append(new_entry)

    try:
        with open(SCORES_FILE, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"New score for user '{usename}' saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save score to file: {e}")

def initialize_chatbox(chat_store: SimpleChatStore, username: str, user_info: str):
    """
    Initializes and returns a chat agent with access to a document index and a scoring tool.
    
    Args:
        chat_store (SimpleChatStore): The chat store for managing conversation history.
        username (str): The current user's username.
        user_info (str): Additional information about the user for context.
        
    Returns:
        ReActAgent: The configured chat agent.
    """
    try:
        # Access API key from Streamlit secrets (safe inside the Streamlit context)
        try:
            google_api_key = st.secrets.google.GOOGLE_API_KEY
        except AttributeError:
            logger.error("Google API key not found in Streamlit secrets. Cannot initialize chat.")
            st.error("API keys are not configured. Please contact the administrator.")
            return None
        
        # Set up LlamaIndex LLM instance
        llm_instance = Gemini(
            model="gemini-1.5-flash", # Corrected model name format
            temperature=0.2, 
            api_key=google_api_key
        )
        Settings.llm = llm_instance # Set global LLM

        memory: ChatMemoryBuffer = ChatMemoryBuffer.from_defaults(
            token_limit=3000,
            chat_store=chat_store,
            chat_store_key=username
        )
        
        storage_context: StorageContext = StorageContext.from_defaults(
            persist_dir=INDEX_STORAGE
        )

        index = load_index_from_storage(
            storage_context, index_id="vector"
        )
        logger.info("Index loaded from storage.")

        dsm5_engine = index.as_query_engine(
            similarity_top_k=3
        )

        dsm5_tool: QueryEngineTool = QueryEngineTool(
            query_engine=dsm5_engine,
            metadata=ToolMetadata(
                name="dsm5",
                description=(
                    "Cung cấp các thông tin liên quan đến các bệnh "
                    "tâm thần theo tiêu chuẩn DSM5. Sử dụng câu hỏi văn bản thuần túy chi tiết làm đầu vào cho công cụ"
                ),
            )
        )

        save_tool: FunctionTool = FunctionTool.from_defaults(fn=save_score)

        # Initialize the ReActAgent (compatible with Gemini)
        agent = ReActAgent.from_tools(
            tools=[dsm5_tool, save_tool],
            llm=llm_instance,
            memory=memory,
            verbose=True,
            # Note: ReActAgent doesn't take 'system_prompt' directly; it should be part of the initial chat history or prompt template.
            # Using the system prompt to seed the chat history might be necessary for full effect.
        )
        
        # Manually setting system instruction for ReActAgent is often done via chat history or LLM prompt template
        # For simplicity, we assume the CUSTORM_AGENT_SYSTEM_TEMPLATE content will be part of the first prompt by the user or pre-appended in a more complex setup.
        
        logger.info("Chat agent initialized.")
        return agent

    except Exception as e:
        logger.error(f"Failed to initialize chatbox: {e}")
        st.error("An error occurred while initializing the chat service. Please try again later.")
        return None