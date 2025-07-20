# RAG 应用：本地知识库问答系统

这是一个基于检索增强生成（RAG）技术的本地知识库问答应用。它使用大型语言模型（LLM）和本地存储的文档，来回答用户提出的问题。

## 功能

- **本地文档处理**：能够读取本地 PDF 文件（如项目中的《内科学》），提取文本内容，并生成向量嵌入。
- **向量化存储**：使用 `Chroma` 向量数据库，将文档内容的向量化表示持久化存储在本地。
- **智能问答**：用户输入问题后，系统首先从向量数据库中检索最相关的内容片段。
- **生成答案**：将检索到的内容和用户的问题一起发送给大型语言模型（本项目使用 DashScope 的 `qwen-turbo`），生成精准的回答。
- **Web 界面**：通过 `Gradio` 提供一个简单直观的用户界面，用户可以方便地输入问题，并同时看到模型生成的答案和所依据的原文内容。

## 技术栈

- **核心框架**：`LangChain`
- **Web 界面**：`Gradio`
- **LLM 服务**：`DashScope` (Qwen-Turbo)
- **嵌入模型**：`DashScope` (text-embedding-v4)
- **向量数据库**：`Chroma`

## 项目结构

```
.
├── know_le/                # 知识库文件夹
│   ├── embds/              # 向量嵌入存储目录
│   └── pdfs/               # 存放原始 PDF 文件
├── .env                    # 环境变量文件，用于存储 API 密钥
├── .gitignore              # Git 忽略文件配置
├── app.py                  # Gradio 应用主程序
├── store.py                # 数据处理脚本，用于读取 PDF 并存入向量数据库
├── pyproject.toml          # 项目依赖配置文件
└── README.md               # 本文档
```

## 安装与运行

**1. 克隆项目**

```bash
git clone <repository-url>
cd rag_rong
```

**2. 安装依赖**

项目使用 `uv` 或 `pip` 管理依赖。请确保您的 Python 版本 >= 3.12。

```bash
pip install -r requirements.txt
# 或者根据 pyproject.toml 手动安装
# pip install gradio langchain langchain_openai langchain_chroma langchain_community dashscope python-dotenv
```

**3. 配置环境变量**

将项目根目录下的 `.env.example` 文件（如果提供）复制为 `.env`，或者直接创建一个 `.env` 文件，并填入您的 API 密钥：

```
DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
OPENAI_API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

**4. 准备知识库**

1.  将您的 PDF 文件放入 `know_le/pdfs/` 文件夹中。
2.  修改 `store.py` 文件，将 `file_path` 变量指向您的 PDF 文件。
3.  运行数据处理脚本，生成向量数据库：

    ```bash
    python store.py
    ```

    **注意**：此脚本只需在更新或更换知识库文档时运行一次。

**5. 启动应用**

```bash
python app.py
```

应用启动后，浏览器会自动打开一个本地网址（通常是 `http://127.0.0.1:7860`），您可以在此界面上进行问答。
