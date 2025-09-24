import openai
from llama_index.core import Settings, Document, VectorStoreIndex
# from llama_index.llms.openai import OpenAI
from llama_index.llms.gemini import Gemini
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.evaluation import (
    BatchEvalRunner,
    CorrectnessEvaluator,
    FaithfulnessEvaluator,
    RelevancyEvaluator
)
from llama_index.core.llama_dataset.generator import RagDatasetGenerator
import asyncio
import pandas as pd
import nest_asyncio
from tqdm.asyncio import tqdm_asyncio


def setup_openai(api_key: str, model: str = "models/gemini-1.5-flash", temperature : float = 0.2 ):
    openai.api_key = api_key
    Settings.llm = Gemini(model=model, temperature= temperature)

#Split text into smaller chunks for processing
def create_document_and_splitter(text : str, chunk_size: int =20 , chunk_overlap : int = 5, separator : str = " "):
    doc = Document(text= text)
    splitter = TokenTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        separator = separator
    )

    nodes = splitter.get_nodes_from_documents([doc])
    return nodes

#Create a vector store index and a query engine
def create_vector_store_index(nodes):
    vector_index = VectorStoreIndex(nodes)
    query_engine = vector_index.as_query_engine()
    return query_engine

def generate_questions(nodes, num_questions_per_chunk: int = 1):
    dataset_generator = RagDatasetGenerator(nodes, num_questions_per_chunk = num_questions_per_chunk)
    eval_questions = dataset_generator.generate_questions_from_nodes()
    return eval_questions.to.pandas()

async def evaluate_async(query_engine, df):
    correctness_evaluator = CorrectnessEvaluator()
    faithfulness_evaluator = FaithfulnessEvaluator()
    relevancy_evaluator = RelevancyEvaluator()

    runner = BatchEvalRunner(
        {
            "correctness": correctness_evaluator,
            "faithfulness": faithfulness_evaluator,
            "relevancy" : relevancy_evaluator
       },
       show_progress = True
    )

    return evaluate_async