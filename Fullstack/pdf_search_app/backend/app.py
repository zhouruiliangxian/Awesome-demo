# -*- coding: utf-8 -*-
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from minio import Minio
from opensearchpy import OpenSearch
import PyPDF2
import io

# --- Initialization ---
load_dotenv()

app = Flask(__name__)
# Enable CORS for React frontend (adjust in production)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# --- Client Connections ---

# OpenSearch Client
opensearch_client = OpenSearch(
    hosts=[{'host': os.getenv('OPENSEARCH_HOST'), 'port': int(os.getenv('OPENSEARCH_PORT'))}],
    http_auth=None,
    use_ssl=False,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)

# MinIO Client
minio_client = Minio(
    os.getenv('MINIO_ENDPOINT'),
    access_key=os.getenv('MINIO_ACCESS_KEY'),
    secret_key=os.getenv('MINIO_SECRET_KEY'),
    secure=False # Set to True if using HTTPS
)

import time

# --- Helper Functions ---

def setup_minio_and_opensearch():
    """Ensure MinIO bucket and OpenSearch index exist, with retries."""
    max_retries = 5
    retry_delay = 3 # seconds

    # Setup MinIO
    for i in range(max_retries):
        try:
            bucket_name = os.getenv('MINIO_BUCKET')
            found = minio_client.bucket_exists(bucket_name)
            if not found:
                minio_client.make_bucket(bucket_name)
                print(f"MinIO bucket '{bucket_name}' created.")
            else:
                print(f"MinIO bucket '{bucket_name}' already exists.")
            break # Success, exit loop
        except Exception as e:
            print(f"MinIO setup failed (attempt {i+1}/{max_retries}): {e}")
            if i + 1 == max_retries:
                raise
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    # Setup OpenSearch (can also have a retry loop if needed)
    index_name = os.getenv('OPENSEARCH_INDEX')
    if not opensearch_client.indices.exists(index=index_name):
        opensearch_client.indices.create(index=index_name)
        print(f"OpenSearch index '{index_name}' created.")
    else:
        print(f"OpenSearch index '{index_name}' already exists.")

def extract_text_from_pdf(pdf_file):
    """Extracts text content from a PDF file stream."""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return None
    return text

# --- API Routes ---

@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Invalid file, please upload a PDF"}), 400

    try:
        # Read file into memory
        pdf_bytes = file.read()
        pdf_stream = io.BytesIO(pdf_bytes)
        file_length = len(pdf_bytes)
        file_name = file.filename

        # 1. Upload original PDF to MinIO
        minio_bucket = os.getenv('MINIO_BUCKET')
        minio_client.put_object(
            minio_bucket,
            file_name,
            pdf_stream,
            length=file_length,
            content_type='application/pdf'
        )
        print(f"Successfully uploaded '{file_name}' to MinIO bucket '{minio_bucket}'.")

        # 2. Extract text from PDF
        pdf_stream.seek(0) # Reset stream position after upload
        extracted_text = extract_text_from_pdf(pdf_stream)
        if extracted_text is None:
            return jsonify({"error": "Could not extract text from PDF"}), 500

        # 3. Index metadata and text into OpenSearch
        document = {
            'file_name': file_name,
            'minio_path': f"/{minio_bucket}/{file_name}",
            'content': extracted_text,
            'size_bytes': file_length
        }
        opensearch_index = os.getenv('OPENSEARCH_INDEX')
        opensearch_client.index(
            index=opensearch_index,
            body=document,
            refresh=True # Make it immediately searchable
        )
        print(f"Successfully indexed metadata for '{file_name}' in OpenSearch.")

        return jsonify({
            "message": "File uploaded and indexed successfully!",
            "file_name": file_name,
            "minio_path": document['minio_path']
        }), 201

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

# --- Main Execution ---

if __name__ == '__main__':
    with app.app_context():
        setup_minio_and_opensearch()
    app.run(host='0.0.0.0', port=5001, debug=True)
