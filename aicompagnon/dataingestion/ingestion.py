import openai
import qdrant_client

from decouple import config

from llama_index.core import (Settings,PromptTemplate)
from llama_index.core import SimpleDirectoryReader
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.core.node_parser import SemanticSplitterNodeParser

from llama_index.llms.openai import OpenAI

from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.readers.web import SimpleWebPageReader

from llama_index.embeddings.openai import OpenAIEmbedding
import tempfile

openai.api_key = config("OPENAI_API_KEY")

Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1, )
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Node Parser
splitter = SemanticSplitterNodeParser(
    buffer_size=1, 
    breakpoint_percentile_threshold=95, 
    embed_model=Settings.embed_model
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


class FileIngestion:
    def __init__(self, dir: str, bot_id: str):
        self.dir = dir
        self.bot_id = bot_id
        
        vector_store = QdrantVectorStore(client=client, collection_name=bot_id)
        self.index = VectorStoreIndex.from_vector_store(vector_store=vector_store, node_parser=splitter)

    def ingest(self):
        # import pdb; pdb.set_trace()
        reader = SimpleDirectoryReader(input_dir=self.dir)
        documents = reader.load_data()
        for doc in documents:
            self.index.insert(doc)