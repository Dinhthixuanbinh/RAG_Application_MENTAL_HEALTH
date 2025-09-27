# src/ingest_pipeline.py

from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import SummaryExtractor
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import Settings 

from llama_index.llms.gemini import Gemini
import google.generativeai as genai
import os # Added for environment variable access
import streamlit as st 
from loguru import logger # Added for logging
from src.global_settings import STORAGE_PATH,FILES_PATH,CACHE_FILE
from src.prompts import CUSTORM_SUMMARY_EXTRACT_TEMPLATE


def get_google_api_key():
    """Retrieves the Google API key from environment variable or Streamlit secrets."""
    # 1. Try to read from environment variable (preferred for standalone scripts)
    key = os.getenv("GOOGLE_API_KEY")
    if key:
        return key

    # 2. Try to read from Streamlit secrets (only works when run via 'streamlit run')
    try:
        # Check if Streamlit is running before trying to access st.secrets
        if st._is_running_with_streamlit:
            key = st.secrets.google.GOOGLE_API_KEY
            return key
    except Exception:
        # st.secrets access failed, which is expected when running as a standalone script
        pass 
        
    return None

google_api_key = get_google_api_key()

if not google_api_key:
    logger.error("GOOGLE_API_KEY not found in environment or Streamlit secrets.")
    # Raise an error to halt execution if the key is missing during ingestion.
    raise EnvironmentError("GOOGLE_API_KEY must be set to run the ingestion pipeline.")

# Configure the underlying Google GenAI client
genai.configure(api_key=google_api_key)

# Configure LlamaIndex Settings
Settings.llm = Gemini(
    model="gemini-2.0-flash", # Changed back to 1.5-flash for compatibility with public API unless 2.0 is confirmed available to you
    temperature=0.2, 
    api_key=google_api_key
)
Settings.embed_model = GeminiEmbedding(
    model_name="embedding-001",
    api_key=google_api_key
)


def ingest_documents():
    """Loads documents, creates ingestion pipeline, runs transformations, and returns nodes."""
    
    documents = SimpleDirectoryReader(
        input_files = FILES_PATH,
        filename_as_id = True, 
    ).load_data()

    for doc in documents:
        logger.info(f"Loaded document ID: {doc.id_}")

    # --- CORRECTION START ---
    # Initialize the variable before the try block to ensure it always has a value
    cached_hashes = "" 
    
    try:
        # If this succeeds, it will overwrite the initial "" value
        cache_hashes = IngestionCache.from_persist_path(
            CACHE_FILE
        )
        logger.info("Cache file found. Running using cache...")

    except FileNotFoundError:
        # This is the expected exception if the cache file doesn't exist.
        logger.info("No cache file found. Running without cache...")
    except Exception as e:
        # Handle unexpected errors gracefully, but proceed without cache
        logger.warning(f"Unexpected error loading cache: {e}. Running without cache.")
        # cached_hashes remains ""
        
    # --- CORRECTION END ---
    
    pipeline = IngestionPipeline(
        transformations = [
            TokenTextSplitter(
                chunk_size= 512,
                chunk_overlap = 20
            ),
            SummaryExtractor(summaries = ['self'], prompt_template = CUSTORM_SUMMARY_EXTRACT_TEMPLATE),
        ],
        cache = cached_hashes # 'cached_hashes' is guaranteed to have a value here
    )

    nodes = pipeline.run(documents = documents)
    pipeline.cache.persist(CACHE_FILE)
    logger.info(f"Ingestion pipeline finished. {len(nodes)} nodes created.")

    return nodes