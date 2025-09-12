from llama_index.core import VectorStoreIndex, Load_index_from_storage
from llama_index.core import StorageContext
from src.global_settings import INDEX_STORAGE


def build_indexes(nodes):
    try:
        storage_context = StorageContext.from_defaults (
            persist_dir = INDEX_STORAGE
        )
        vector_index = Load_index_from_storage(
            storage_context, index_id = "vector"
        )

        print("all indices loaded  from storage. ")
    except Exception as e:
        print(f"Error occured while loading indices: {e}")
        storage_context = StorageContext.from_dafaults()
        vector_index = VectorStoreIndex(
            nodes, storage_context = storage_context
        )
        vector_index.set_index_id("vector")
        storage_context.persist(
            persist_dir = INDEX_STORAGE
        )
        print("New indexes created and persisted")
    
    return vector_index