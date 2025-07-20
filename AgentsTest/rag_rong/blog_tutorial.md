# 博客教程：从零开始构建一个本地知识库问答机器人

在本教程中，我们将一步步地构建一个完整的“检索增强生成” (RAG) 应用。这个应用可以读取您本地的 PDF 文档，并利用大型语言模型（LLM）来回答关于这些文档的任何问题。最终，我们将拥有一个带 Web 界面的问答机器人。

![最终效果图](https://i.imgur.com/your-final-app-image.png) <!-- 你可以将最终应用的截图链接放在这里 -->

## 项目简介

我们将创建一个系统，它包含两个核心部分：

1.  **数据处理**：一个脚本，负责读取 PDF 文档，将其内容分割、向量化，并存入一个本地的向量数据库中。
2.  **问答应用**：一个带有 Gradio 界面的 Web 应用。用户输入问题后，它会从数据库中检索相关信息，然后连同问题一起交给 LLM，最终生成精准的答案。

## 技术栈

- **Python 版本**: 3.12+
- **环境与包管理**: `uv` (一个极速的 Python 包安装器和解析器)
- **核心 AI 框架**: `LangChain`
- **Web UI**: `Gradio`
- **向量数据库**: `ChromaDB`
- **LLM 与嵌入**: `DashScope` (阿里云灵积模型服务)

---

## 第一步：环境初始化与项目设置

首先，我们需要为项目创建一个干净的 Python 环境。

**1. 创建项目文件夹**

打开您的终端，创建一个新的文件夹并进入该目录。

```bash
mkdir rag-tutorial
cd rag-tutorial
```

**2. 初始化虚拟环境**

我们将使用 `uv` 来管理虚拟环境和依赖。如果您尚未安装 `uv`，请参考其[官方文档](https://github.com/astral-sh/uv)进行安装。

运行以下命令来创建一个虚拟环境：

```bash
uv init
```

这条命令会创建一个 `pyproject.toml` 文件，用于定义项目依赖，同时也会在当前目录下生成一个 `.venv` 的虚拟环境文件夹。

**3. 激活虚拟环境**

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

激活后，您应该会在终端提示符前看到 `(.venv)` 的字样。

## 第二步：安装所有依赖

现在，我们来安装项目所需的所有 Python 库。

```bash
uv pip install gradio langchain langchain_openai langchain_chroma langchain_community dashscope python-dotenv pypdf
```

`uv` 会将这些依赖项及其版本信息自动记录到 `pyproject.toml` 文件中。

## 第三步：创建项目结构

一个清晰的目录结构有助于我们管理项目。请在项目根目录下创建以下文件夹：

```bash
mkdir -p know_le/pdfs
mkdir -p know_le/embds
```

- `know_le/pdfs`: 用于存放您希望机器人学习的原始 PDF 文件。
- `know_le/embds`: 用于存放 ChromaDB 生成的向量数据库文件。

现在，请将您想用的 PDF 文件（例如，一本专业书籍、一份产品手册等）放入 `know_le/pdfs` 文件夹中。

## 第四步：安全地管理 API 密钥

为了连接 DashScope 的 LLM 服务，我们需要 API 密钥。将密钥硬编码在代码中是非常不安全的做法。我们将使用 `.env` 文件来管理它们。

**1. 创建 `.env` 文件**

在项目根目录下创建一个名为 `.env` 的文件，并填入以下内容。请将 `sk-xxx` 替换为您自己的 DashScope API 密钥。

```dotenv
# .env

DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
OPENAI_API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

**2. 创建 `.gitignore` 文件**

为了防止您不小心将含有密钥的 `.env` 文件提交到 Git 仓库，我们创建一个 `.gitignore` 文件来忽略它。

```gitignore
# .gitignore

# 虚拟环境
.venv/

# 环境变量文件
.env

# IDE 和系统文件
.idea/
__pycache__/
*.pyc
```

## 第五步：编写数据处理脚本 (`store.py`)

这个脚本是一次性运行的，它的任务是读取 PDF，处理文本，并将其存储到向量数据库中。

在项目根目录创建 `store.py` 文件，并粘贴以下代码：

```python
# store.py

import os
import asyncio
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from langchain.vectorstores import Chroma

# 从 .env 文件加载环境变量
load_dotenv()

# --- 配置路径 ---
# 将这里的路径替换为您自己的 PDF 文件路径
PDF_FILE_PATH = r"know_le/pdfs/21. 内科学（第10版）n.pdf"
# ChromaDB 的持久化存储路径
PERSIST_DIRECTORY = r"know_le/embds/a21"

def main():
    """主函数，用于处理 PDF 并存入向量数据库"""
    print("开始加载 PDF 文档...")
    loader = PyPDFLoader(PDF_FILE_PATH)
    pages = loader.load_and_split() # 直接加载并分割文档
    print(f"文档加载并分割完成，共 {len(pages)} 页。")

    print("初始化嵌入模型...")
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v4",
    )

    print("正在创建并持久化向量数据库...")
    # 从文档创建 Chroma 向量存储，并指定持久化目录
    vector_store = Chroma.from_documents(
        documents=pages, 
        embedding=embeddings, 
        collection_name="a21", # 自定义集合名称
        persist_directory=PERSIST_DIRECTORY
    )
    print("向量数据库创建并保存成功！")

    print("\n--- 测试检索功能 ---")
    # 测试一下数据库是否能正常工作
    docs = vector_store.similarity_search("什么是内科学", k=2)
    for doc in docs:
        print(f"检索到相关页面 {doc.metadata.get('page', 'N/A')}:\n{doc.page_content[:200]}\n")

if __name__ == "__main__":
    main()

```

**代码解释**:
- `load_dotenv()`: 从 `.env` 文件加载我们配置的 API 密钥。
- `PyPDFLoader`: LangChain 提供的一个工具，专门用来加载和解析 PDF 文件。
- `DashScopeEmbeddings`: 将文本转换为向量的嵌入模型。
- `Chroma.from_documents`: 这个函数接收处理好的文档和嵌入模型，然后创建向量数据库。通过设置 `persist_directory`，它会将数据库文件保存在我们指定的文件夹中，以便主应用可以重复使用。

## 第六步：编写主应用 (`app.py`)

这是我们的问答机器人主程序，它将启动一个 Gradio Web 界面。

在项目根目录创建 `app.py` 文件，并粘贴以下代码：

```python
# app.py

import os
import sys
import gradio as gr
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_community.embeddings.dashscope import DashScopeEmbeddings

# 加载环境变量
load_dotenv()

# --- 模型和数据库初始化 ---

# 初始化 LLM
llm = ChatOpenAI(
    temperature=0,
    model="qwen-turbo",
    openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE")
)

# 初始化嵌入模型
embeddings = DashScopeEmbeddings(model="text-embedding-v4")

# 加载持久化的向量数据库
vectorstore = Chroma(
    collection_name="a21",
    persist_directory="know_le/embds/a21",
    embedding_function=embeddings
)

# 初始化检索器
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2}, # 检索最相关的 2 个文档
)

# --- RAG 链定义 ---

# 定义提示模板
message = """
基于以下已知信息，简洁和专业地回答用户的问题。
如果无法从中得到答案，请说 “根据已知信息无法回答该问题”，不允许在答案中添加编造成分，答案请使用中文。

问题：
{question}

已知信息：
{context}
"""
prompt = ChatPromptTemplate.from_messages([("human", message)])

# 定义 RAG 链
rag_chain = (
    RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
    | prompt
    | llm
)

# --- Gradio 界面 ---

def get_response(question):
    """获取模型响应的函数"""
    # 使用 RAG 链获取响应
    response = rag_chain.invoke(question)
    return response.content

iface = gr.Interface(
    fn=get_response,
    inputs=gr.Textbox(lines=2, placeholder="请输入您关于文档的问题..."),
    outputs=gr.Markdown(label="模型回答"),
    title="本地知识库 RAG 问答机器人",
    description="输入一个问题，模型将基于本地 PDF 文档内容进行回答。"
)

if __name__ == "__main__":
    print("正在启动 Gradio 界面...")
    iface.launch()

```

**代码解释**:
- **加载数据库**: 与 `store.py` 不同，这里我们直接使用 `Chroma(...)` 来加载已经存在的数据库，而不是 `from_documents`。
- **Retriever**: 检索器是连接数据库和 RAG 链的桥梁，它负责根据输入的问题从数据库中找出相关的文档。
- **RAG Chain**: 这是 LangChain 的核心。我们定义了一个处理流程：
    1.  并行地，用 `retriever` 获取上下文 (`context`)，并把用户的问题 (`question`) 传递下去。
    2.  将获取到的 `context` 和 `question` 填入我们定义的 `prompt` 模板中。
    3.  最后将格式化好的提示发送给 `llm` 生成最终答案。
- **Gradio Interface**: `gr.Interface` 快速创建一个 Web UI，`fn` 参数是我们定义的响应函数，`inputs` 和 `outputs` 定义了输入输出组件。

## 第七步：运行你的 RAG 应用

现在，万事俱备！

**1. 生成数据库**

首先，我们需要运行一次 `store.py` 来处理我们的 PDF 文件并创建数据库。

```bash
uv run store.py
```

您应该会看到脚本成功运行的日志。这个步骤只需要在您添加或更新 PDF 文件时才需要重复执行。

**2. 启动问答应用**

现在，启动我们的主应用。

```bash
uv run app.py
```

终端会显示 Gradio 正在运行，并提供一个本地 URL (例如 `http://127.0.0.1:7860`)。在浏览器中打开这个地址，您就可以开始和您的知识库问答机器人对话了！

## 总结与展望

恭喜！您已经成功构建并运行了一个功能齐全的 RAG 应用。您学会了如何：

- 设置和管理 Python 项目环境。
- 使用 LangChain 处理和存储文档。
- 构建一个完整的 RAG 链。
- 使用 Gradio 创建一个简单的 Web 界面。

从这里开始，您可以尝试更多扩展，例如：
- 在 `know_le/pdfs` 中添加更多的文档。
- 调整 `retriever` 的 `search_kwargs` 参数来改变检索行为。
- 替换成其他的大型语言模型或嵌入模型。

希望这篇教程对您有所帮助！
