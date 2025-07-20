from langchain_community.document_loaders import PyPDFLoader
import asyncio

from langchain.vectorstores import Chroma

file_path = r"D:\agent-llm\rag_rong\know_le\pdfs\21. 内科学（第10版）n.pdf"
persist_directory = r"D:\agent-llm\rag_rong\know_le\embds\a21"


loader = PyPDFLoader(file_path)
pages = []

async def load_pages():
    async for page in loader.alazy_load():
        pages.append(page)

# Run the async function
asyncio.run(load_pages())

print(len(pages))
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain_community.embeddings.dashscope import DashScopeEmbeddings
embeddings = DashScopeEmbeddings(
    model="text-embedding-v4",
)


vector_store = Chroma.from_documents(pages, embeddings ,collection_name="a21",persist_directory=persist_directory)
docs = vector_store.similarity_search("什么是内科学", k=2)
for doc in docs:
    print(f"Page {doc.metadata['page']}: {doc.page_content[:300]}\n")

