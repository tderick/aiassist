import openai
import qdrant_client
from decouple import config

from llama_index.core import (Settings,PromptTemplate)
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.core.indices.vector_store.base import VectorStoreIndex

from llama_index.vector_stores.qdrant import QdrantVectorStore

from llama_index.embeddings.openai import OpenAIEmbedding

openai.api_key = config("OPENAI_API_KEY")

Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")


# Node Parser
splitter = SemanticSplitterNodeParser(
    buffer_size=1, 
    breakpoint_percentile_threshold=95, 
    embed_model=Settings.embed_model
)

# Qdrant Vector Store
client = qdrant_client.QdrantClient("localhost", port=6333)

# template = (
#     "We have provided context information below. If there is no relevant information in the context, say you don't know the answer. It is a very important point to follow strictly \n"
#     "---------------------\n"
#     "{context_str}"
#     "\n---------------------\n"
#     "Given the context information and not prior knowledge, and by providing the source from the context "
#     "answer the query, please answer the question: {query_str}\n"
# )
# qa_template = PromptTemplate(template)

class DataRetrieval:
    def __init__(self, question: str , bot_id: str):
      self.question = question
      self.bot_id = bot_id
        
      vector_store = QdrantVectorStore(client=client, collection_name=bot_id)
      self.index = VectorStoreIndex.from_vector_store(vector_store=vector_store, node_parser=splitter)

    def retrieve(self):
        # query_engine = self.index.as_query_engine(similarity_top_k=10, logging_level="INFO", prompt_template=qa_template, temperature=0.1)
        query_engine = CitationQueryEngine.from_args(
            self.index,
            similarity_top_k=3,
            # here we can control how granular citation sources are, the default is 512
            citation_chunk_size=1024,
        )
        response = query_engine.query(self.question)
        return response.response

