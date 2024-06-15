import openai
from decouple import config

import qdrant_client

from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding

openai.api_key = config("OPENAI_API_KEY")

# Node Parser
embed_model = OpenAIEmbedding()
splitter = SemanticSplitterNodeParser(
    buffer_size=1, 
    breakpoint_percentile_threshold=95, 
    embed_model=embed_model
)

# Qdrant Vector Store
client = qdrant_client.QdrantClient("localhost", port=6333)


class DataRetrieval:
    def __init__(self, question: str , bot_id: str):
      self.question = question
      self.bot_id = bot_id
        
      vector_store = QdrantVectorStore(client=client, collection_name=bot_id)
      self.index = VectorStoreIndex.from_vector_store(vector_store=vector_store, node_parser=splitter)

    def retrieve(self):
        query_engine = self.index.as_query_engine(similarity_top_k=10, logging_level="INFO")
        response = query_engine.query(self.question)
        return response.response

