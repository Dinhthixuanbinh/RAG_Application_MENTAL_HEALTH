# src/index_builder.py 
from llama_index.core import VectorStoreIndex, load_index_from_storage # Corrected Load_index_from_storage capitalization
from llama_index.core import StorageContext
from src.global_settings import INDEX_STORAGE
from loguru import logger 
# Note: Corrected the import capitalization from Load_index_from_storage to load_index_from_storage

def build_indexes(nodes):
    """
    Builds or loads a vector store index and persists it to disk.
    """
    vector_index = None
    try:
        # Try to load existing index
        storage_context = StorageContext.from_defaults(
            persist_dir = INDEX_STORAGE
        )
        vector_index = load_index_from_storage(
           storage_context, index_id = "vector"
        )

        logger.info("All indices loaded from storage.")
    except Exception as e:
        logger.warning(f"Error occurred while loading indices: {e}. Building new index.")
        
        # --- CORRECTION APPLIED HERE ---
        # Changed 'from_dafaults()' to 'from_defaults()'
        storage_context = StorageContext.from_defaults()
        # --- END OF CORRECTION ---
        
        # Build new index
        vector_index = VectorStoreIndex(
            nodes, storage_context = storage_context
        )
        vector_index.set_index_id("vector")
        
        # Persist new index
        try:
            storage_context.persist(
                persist_dir = INDEX_STORAGE
            )
            logger.success("New indexes created and persisted.")
        except Exception as persist_e:
             logger.error(f"Failed to persist new indexes: {persist_e}")
             
    return vector_index