import os
from pymongo import MongoClient
from llama_index.core import VectorStoreIndex, StorageContext, Settings, Document
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from db_connection import uri
import time

Settings.llm = Ollama(model="llama3.2",request_timeout=120.0,timeout=120.0)
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

MONGO_URI = uri
DB_NAME = "rooms_db"

mongodb_client = MongoClient(MONGO_URI)
db = mongodb_client[DB_NAME]
# source_collection = db["vectors_collection"]

# documents = []
# for room in source_collection.find({}):
#     room_id = str(room.get("id", ""))
#     name = str(room.get("name", ""))
#     description = str(room.get("description", ""))
#     price = str(room.get("price", ""))
    
#     clean_text = f"Room ID: {room_id} | Name: {name} | Description: {description} | Price: ${price}"

#     doc = Document(
#         text=clean_text,
#         metadata={
#             "room_id": room_id,
#             "name": name,
#             "description":description,
#             "price": price
#         }
#     )
#     documents.append(doc)

# print(f"Loaded {len(documents)} documents from MongoDB")

# Reads directly from vectors collection instead of inputting new records every time

def show_rooms(query:str):
    source_collection = db["vectors_collection"]

    vector_store = MongoDBAtlasVectorSearch(
        mongodb_client=mongodb_client,
        db_name=DB_NAME,
        collection_name="vectors_collection", 
        vector_index_name="default" 
    )


    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context
    )
    # index = VectorStoreIndex.from_documents(
    #     documents,
    #     storage_context=storage_context
    # )
    # print(index)

    retriever = index.as_retriever(similarity_top_k=9)
    nodes = retriever.retrieve(query)
    # print(retriever)

    # print(f"\nNodes Retrieved: {len(nodes)}")
    # for i, node in enumerate(nodes):
    #     print("test")
    #     print(f"Node {i+1} [Score: {node.score}]: {node.node.get_content()}")

    query_engine = index.as_query_engine(similarity_top_k=10,similarity_threshold=0)
    response = query_engine.query(query)


    return str(response)

    # print("\nResponse")
    # print(response)

    # vectors_collection = db["vectors_collection"]
    # print("Documents in vector collection:",vector_store._collection.count_documents({}))

    # print("\nRetrieved Nodes Count")
    # print(len(response.source_nodes))

# print(show_rooms("Show big rooms"))
# print("=== DEBUG INFO ===")
# print("Documents count:", vector_store._collection.count_documents({}))

# # Sample document check
# sample = vector_store._collection.find_one({})
# if sample:
#     print("Sample keys:", list(sample.keys()))
#     if "embedding" in sample:
#         emb = sample["embedding"]
#         print(f"Embedding dimensions: {len(emb)}")
#         print(f"First few values: {emb[:5]}")
#     else:
#         print("No 'embedding' field found!")

#     # Check metadata
#     print("Sample metadata:", sample.get("metadata", {}))
# else:
#     print("No documents found")

# # List all search indexes
# try:
#     indexes = list(vector_store._collection.list_search_indexes())
#     print(f"\nSearch Indexes ({len(indexes)} found):")
#     for idx in indexes:
#         print(f" Name: {idx.get('name')}")
#         print(f" Status: {idx.get('status')}")
#         print(f" Type: {idx.get('type')}")
#         print("---")
# except Exception as e:
#     print("Error listing indexes:", str(e))


