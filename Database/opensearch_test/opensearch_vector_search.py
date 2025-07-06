# -*- coding: utf-8 -*-

"""
This script demonstrates how to perform vector storage and search in OpenSearch.

It requires the following libraries:
- opensearch-py
- sentence-transformers

You can install them using: pip install opensearch-py sentence-transformers
"""

import time
from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer

# --- 1. Configuration ---

# Connect to OpenSearch
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=None,  # No authentication as per docker-compose.yml
    use_ssl=False,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)

# Load a pre-trained sentence transformer model
# all-MiniLM-L6-v2 is a fast and solid model for semantic search.
model = SentenceTransformer('all-MiniLM-L6-v2')
# The dimension of the vectors produced by this model is 384
VECTOR_DIMENSION = 384

INDEX_NAME = "my-vector-test-index"


# --- 2. Index Setup ---

def create_index_with_vector_mapping():
    """Creates an OpenSearch index with a mapping for k-NN vector search."""
    if client.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists. Deleting it.")
        client.indices.delete(index=INDEX_NAME)

    settings = {
        "settings": {
            "index": {
                "knn": True, # Enable k-NN search functionality
                "knn.algo_param.ef_search": 100
            }
        },
        "mappings": {
            "properties": {
                "text": {"type": "text"}, # Standard text field
                "text_vector": { # Vector field for k-NN search
                    "type": "knn_vector",
                    "dimension": VECTOR_DIMENSION,
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
    client.indices.create(index=INDEX_NAME, body=settings)
    print(f"Index '{INDEX_NAME}' created successfully.")


# --- 3. Indexing Documents ---

def index_documents():
    """Generates vector embeddings for sample documents and indexes them."""
    documents = [
        {"text": "The sky is blue and the sun is bright."}, # 天空是蓝色的，太阳很明亮。
        {"text": "I enjoy walking in the park on a sunny day."}, # 我喜欢在晴天公园散步。
        {"text": "Artificial intelligence is transforming many industries."}, # 人工智能正在改变许多行业。
        {"text": "The new AI model shows impressive capabilities in natural language understanding."}, # 新的AI模型在自然语言理解方面表现出色。
        {"text": "My favorite food is pizza, especially with pepperoni."}, # 我最喜欢的食物是披萨，特别是意大利辣香肠披萨。
        {"text": "I'm planning a trip to Italy to enjoy the local cuisine."}
    ]

    for i, doc in enumerate(documents):
        # Generate the vector embedding for the text
        vector = model.encode(doc["text"])
        
        # Create the document body for indexing
        doc_body = {
            "text": doc["text"],
            "text_vector": vector.tolist() # Convert numpy array to list
        }
        
        # Index the document
        client.index(index=INDEX_NAME, body=doc_body, id=i+1, refresh=True)
        print(f"Indexed document {i+1}")

    # Give OpenSearch some time to make the documents searchable
    time.sleep(2)


# --- 4. Vector Search ---

def search_with_vector(query_text, k=3):
    """Performs a k-NN search for the most similar documents."""
    print(f"\n--- Performing k-NN search for: '{query_text}' ---")
    
    # Generate the vector for the query text
    query_vector = model.encode(query_text).tolist()
    
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
    
    response = client.search(index=INDEX_NAME, body=search_query)
    
    print("Search Results:")
    for hit in response["hits"]["hits"]:
        print(f"  - Score: {hit['_score']:.4f}, Text: {hit['_source']['text']}")


def hybrid_search(query_text, filter_keyword, k=2):
    """Performs a hybrid search combining k-NN and a boolean filter."""
    print(f"\n--- Performing Hybrid search for: '{query_text}' with filter '{filter_keyword}' ---")

    query_vector = model.encode(query_text).tolist()

    search_query = {
        "size": k,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "text": filter_keyword
                        }
                    }
                ],
                "should": [
                    {
                        "knn": {
                            "text_vector": {
                                "vector": query_vector,
                                "k": k
                            }
                        }
                    }
                ]
            }
        }
    }

    response = client.search(index=INDEX_NAME, body=search_query)

    print("Search Results:")
    if not response["hits"]["hits"]:
        print("  No documents found.")
    for hit in response["hits"]["hits"]:
        print(f"  - Score: {hit['_score']:.4f}, Text: {hit['_source']['text']}")


# --- 5. Main Execution ---
if __name__ == "__main__":
    # Create index and mapping
    create_index_with_vector_mapping()
    
    # Index some documents
    index_documents()
    
    # Perform a simple vector search
    search_with_vector("intelligent machines") # 查询 “智能机器”
    
    # Perform another vector search
    search_with_vector("sunny weather activities") # 查询 “晴天活动”

    # Perform a hybrid search (combining vector and keyword)
    hybrid_search("places to eat", filter_keyword="italy") # 查询 “吃饭的地方”，并筛选包含 “italy” 的结果

    # Clean up the index
    # client.indices.delete(index=INDEX_NAME)
    # print(f"\nIndex '{INDEX_NAME}' deleted.")
