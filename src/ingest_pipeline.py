from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import SummaryExtractor
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import Settings 

# from llama_index.llms.openai import OpenAI
from llama_index.llms.gemini import Gemini
# import openai 
import google.generativeai as genai

import streamlit as st
from src.global_settings import STORAGE_PATH,FILES_PATH,CACHE_FILE
from src.prompts import CUSTORM_SUMMARY_EXTRACT_TEMPLATE


# openai.api_key = st.secrets.openai.OPEN_API_KEY
genai.configure(api_key=st.secrets.google.GOOGLE_API_KEY)
Settings.llm = Gemini(model="models/gemini-1.5-flash", temperature = 0.2, api_key=st.secrets.google.GOOGLE_API_KEY)
# Set up the embedding model
Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001")
def ingest_documents():
    
    documents = SimpleDirectoryReader(
        imput_files = FILES_PATH,
        filename_as_id = True, 
    ).load_data()

    for doc in documents:
        print(doc.id_)

    try:
        cache_hashes = IngestionCache.from_persist_path(
            CACHE_FILE
        )
        print("Cache file found. Running using cache...")

    except:
        cached_hashes = ""
        print("No cache file found. Running without cache...")
    
    pipeline = IngestionPipeline(
        transformations = [
            TokenTextSplitter(
                chunk_size= 512,
                chunk_overlap = 20
            ),
            SummaryExtractor(summaries = ['self'], prompt_template = CUSTORM_SUMMARY_EXTRACT_TEMPLATE),
            # OpenAIEmbedding()
        ],
        cache = cached_hashes
    )

    nodes = pipeline.run(documents = documents)
    pipeline.cache.persist(CACHE_FILE)


    return nodes 
