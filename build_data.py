# build_data.py
from loguru import logger
from src.index_builder import build_indexes
from src.ingest_pipeline import ingest_documents

def main():
    """
    Main function to run the data ingestion and index building process.
    """
    logger.info("Starting data ingestion and index building...")
    try:
        nodes = ingest_documents()
        build_indexes(nodes)
        logger.success("Data ingestion and index building completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during data processing: {e}")

if __name__ == "__main__":
    main()