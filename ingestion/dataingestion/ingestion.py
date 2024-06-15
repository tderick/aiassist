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
            print(self.index.insert(doc))


# documents = SimpleWebPageReader(html_to_text=True).load_data(
#     ["https://www.unipi.it/index.php/master"]
# )

# import pdb; pdb.set_trace()
# for doc in documents:
# index.insert(documents[0])

# set Logging to DEBUG for more detailed outputs
# query_engine = index.as_query_engine(llm=None, logging_level="INFO")
# response = query_engine.query("what master's are available?")

# print(response)

# RETRIEVAL
# query_engine = index.as_query_engine(
#                   llm=llm,
#                   similarity_top_k=10,
#                 )

# query = "List all the available master's programs at the University of Pisa"
# resp = query_engine.query(query)

# print(resp.response)