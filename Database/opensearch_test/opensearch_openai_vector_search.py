# -*- coding: utf-8 -*-

"""
This script demonstrates how to use OpenAI embeddings for vector search in OpenSearch.

It requires the following libraries:
- opensearch-py
- openai
- python-dotenv

You can install them using: pip install opensearch-py openai python-dotenv

Setup:
1. Make sure your OpenSearch instance is running (e.g., via docker-compose).
2. Create a file named .env in the same directory as this script.
3. Add your OpenAI API key to the .env file like this:
   OPENAI_API_KEY="sk-YourActualOpenAIKeyHere"
"""

import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from opensearchpy import OpenSearch

# --- 1. Configuration ---

# Load environment variables from .env file
load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")
QWEN_EMBEDDING_MODEL_NAME = os.getenv("QWEN_EMBEDDING_MODEL_NAME")

client_openai = OpenAI(base_url=QWEN_BASE_URL, api_key=QWEN_API_KEY)
# Connect to OpenSearch
client_opensearch = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=None,  # No authentication
    use_ssl=False,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)


# Dimension of vectors produced by text-embedding-3-small
VECTOR_DIMENSION = 1024

INDEX_NAME = "my-openai-vector-index"


# --- 2. OpenAI Embedding Function ---

def get_openai_embedding(text):
    """Generates a vector embedding for the given text using OpenAI's API."""
    # OpenAI recommends replacing newlines with spaces for better performance
    text = text.replace("\n", " ")
    response = client_openai.embeddings.create(input=[text], model=QWEN_EMBEDDING_MODEL_NAME)
    return response.data[0].embedding


# --- 3. Index Setup ---

def create_index_with_vector_mapping():
    """Creates an OpenSearch index with a mapping for k-NN vector search using OpenAI dimensions."""
    if client_opensearch.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists. Deleting it.")
        client_opensearch.indices.delete(index=INDEX_NAME)

    settings = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 100
            }
        },
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "text_vector": {
                    "type": "knn_vector",
                    "dimension": VECTOR_DIMENSION, # Crucial: Must match the model's output dimension
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "nmslib",
                        "parameters": {
                            "ef_construction": 128,
                            "m": 24
                        }
                    }
                }
            }
        }
    }
    client_opensearch.indices.create(index=INDEX_NAME, body=settings)
    print(f"Index '{INDEX_NAME}' created successfully with dimension {VECTOR_DIMENSION}.")


# --- 4. Indexing Documents ---

def index_documents():
    """Generates vector embeddings for sample documents using OpenAI and indexes them."""
    documents = [
        {"text": "The sky is blue and the sun is bright."},
        {"text": "I enjoy walking in the park on a sunny day."},
        {"text": "Artificial intelligence is transforming many industries."},
        {"text": "The new AI model shows impressive capabilities in natural language understanding."},
        {"text": "My favorite food is pizza, especially with pepperoni."},
        {"text": "I'm planning a trip to Italy to enjoy the local cuisine."}
    ]

    for i, doc in enumerate(documents):
        print(f"Generating embedding for document {i+1}...")
        vector = get_openai_embedding(doc["text"])
        
        doc_body = {
            "text": doc["text"],
            "text_vector": vector # The embedding is already a list
        }
        
        client_opensearch.index(index=INDEX_NAME, body=doc_body, id=i+1, refresh=True)
        print(f"Indexed document {i+1}")

    time.sleep(2)


# --- 5. Vector Search ---

def search_with_vector(query_text, k=3):
    """Performs a k-NN search for the most similar documents using an OpenAI embedding."""
    print(f"\n--- Performing k-NN search for: '{query_text}' ---")
    
    query_vector = get_openai_embedding(query_text)
    
    search_query = {
        "size": k,
        "query": {
            "knn": {
                "text_vector": {
                    "vector": query_vector,
                    "k": k
                }
            }
        }
    }
    
    response = client_opensearch.search(index=INDEX_NAME, body=search_query)
    
    print("Search Results:")
    for hit in response["hits"]["hits"]:
        print(f"  - Score: {hit['_score']:.4f}, Text: {hit['_source']['text']}")


# --- 6. Main Execution ---
if __name__ == "__main__":
    create_index_with_vector_mapping()
    index_documents()
    
    # Perform a simple vector search
    search_with_vector("intelligent machines")
    
    # Perform another vector search
    search_with_vector("sunny weather activities")

    # Clean up the index (optional)
    # client_opensearch.indices.delete(index=INDEX_NAME)
    # print(f"\nIndex '{INDEX_NAME}' deleted.")
