import openai
from decouple import config

import qdrant_client

from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.readers.web import SimpleWebPageReader

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

class WebPageIngestion:
    def __init__(self, url: str, bot_id: str):
      self.url = url
      self.bot_id = bot_id
        
      vector_store = QdrantVectorStore(client=client, collection_name=bot_id)
      self.index = VectorStoreIndex.from_vector_store(vector_store=vector_store, node_parser=splitter)

    def ingest(self):
        documents = SimpleWebPageReader(html_to_text=True).load_data([self.url])
        for doc in documents:
            self.index.insert(doc)
