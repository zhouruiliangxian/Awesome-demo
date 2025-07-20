
import gradio as gr
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
import os
import sys
from langchain_community.embeddings.dashscope import DashScopeEmbeddings

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    temperature=0,
    model="qwen-turbo",
    openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE")
)

# Initialize Embeddings
# The environment variable is already set by load_dotenv(), so no need to set it again here.
embeddings = DashScopeEmbeddings(model="text-embedding-v4")

# Initialize Chroma Vectorstore
vectorstore = Chroma(
    collection_name="a21",
    persist_directory=resource_path(os.path.join('know_le', 'embds', 'a21')),
    embedding_function=embeddings
)

# Initialize Retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2},
)

# Define Prompt Template
message = """
问题：
{question}

提供内容：
{context}

基于提供的内容，回答问题。
"""
prompt = ChatPromptTemplate.from_messages([("human", message)])

# Define Chains
retrieval_chain = RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
generation_chain = prompt | llm

def get_response(question):
    retrieved_result = retrieval_chain.invoke(question)
    
    retrieved_docs = ""
    for doc in retrieved_result["context"]:
        retrieved_docs += doc.page_content + "\n" + "--------------------" + "\n"

    response = generation_chain.invoke(retrieved_result)
    
    return retrieved_docs, response.content

iface = gr.Interface(
    fn=get_response,
    inputs=gr.Textbox(lines=2, placeholder="请输入您的问题..."),
    outputs=[
        gr.Textbox(label="检索内容"),
        gr.Markdown(label="模型回答")
    ],
    title="RAG 应用",
    description="输入一个问题，同时查看检索到的内容和模型的回答。"
)

if __name__ == "__main__":
    iface.launch()
