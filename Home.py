# Home.py
import streamlit as st
from loguru import logger

def main():
    """
    Main function for the Streamlit Home page.
    """
    st.set_page_config(
        page_title="RAG Application for Mental Health",
        page_icon="🧠",
        layout="wide"
    )

    st.title("🧠 RAG Application for Mental Health")
    st.markdown(
        """
        ### Welcome to the RAG Application for Mental Health!
        
        This application leverages a Retrieval-Augmented Generation (RAG) system 
        to provide information on mental health based on the DSM-5 criteria.

        Navigate to the different sections using the sidebar:
        - **Chat**: Interact with the RAG assistant to get information on mental health topics.
        - **User**: Manage user-related information and settings.
        """
    )

if __name__ == "__main__":
    logger.info("Starting Home.py")
    main()