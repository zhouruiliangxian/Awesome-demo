from opensearchpy import OpenSearch

# Connect to OpenSearch
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=None,  # No authentication
    use_ssl=False,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)

# 1. Create (Index a document)
def create_document(index_name, doc_id, document):
    response = client.index(index=index_name, id=doc_id, body=document)
    print(f"Document created: {response['_id']}")

# 2. Read (Get a document)
def read_document(index_name, doc_id):
    try:
        response = client.get(index=index_name, id=doc_id)
        print(f"Document found: {response['_source']}")
        return response['_source']
    except Exception as e:
        print(f"Error reading document: {e}")
        return None

# 3. Update (Update a document)
def update_document(index_name, doc_id, partial_document):
    response = client.update(index=index_name, id=doc_id, body={"doc": partial_document})
    print(f"Document updated: {response['_id']}")

# 4. Delete (Delete a document)
def delete_document(index_name, doc_id):
    try:
        response = client.delete(index=index_name, id=doc_id)
        print(f"Document deleted: {response['_id']}")
    except Exception as e:
        print(f"Error deleting document: {e}")

# --- Example Usage ---
if __name__ == "__main__":
    INDEX_NAME = "my-test-index"
    DOC_ID = "1"

    # Create
    print("--- Creating document ---")
    my_document = {
        'title': 'The Lord of the Rings',
        'author': 'J.R.R. Tolkien',
        'year': 1954
    }
    create_document(INDEX_NAME, DOC_ID, my_document)

    # Read
    print("\n--- Reading document ---")
    read_document(INDEX_NAME, DOC_ID)

    # Update
    print("\n--- Updating document ---")
    update_payload = {
        'year': 1955 # Correcting the publication year
    }
    update_document(INDEX_NAME, DOC_ID, update_payload)

    # Read again to see the change
    print("\n--- Reading document after update ---")
    read_document(INDEX_NAME, DOC_ID)

    # Delete
    print("\n--- Deleting document ---")
    delete_document(INDEX_NAME, DOC_ID)

    # Try to read again
    print("\n--- Reading document after delete ---")
    read_document(INDEX_NAME, DOC_ID)
