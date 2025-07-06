# PDF 上传与保存到 MinIO 应用

本项目是一个全栈应用，允许用户上传 PDF 文件。后端使用 Flask 构建，它会将原始 PDF 文件存储在 MinIO 存储桶中，并将其提取的文本内容索引到 OpenSearch 中。前端则是一个用于上传文件的简单 React 应用。

## 项目结构

```
pdf_search_app/
├── backend/            # Flask 后端
│   ├── .env            # 后端的环境变量
│   ├── app.py          # 主要的 Flask 应用逻辑
│   └── requirements.txt# Python 依赖项
├── frontend/           # React 前端
│   ├── public/
│   ├── src/
│   │   ├── App.css     # 前端样式文件
│   │   └── App.js      # 主要的 React 组件
│   └── package.json
└── docker-compose.yml  # 用于运行所有服务的 Docker Compose 文件
```

---

## 如何运行本应用

请遵循以下步骤来启动并运行整个应用。

### 第 1 步：启动基础设施服务

`docker-compose.yml` 文件将会启动 OpenSearch、OpenSearch Dashboards 和 MinIO。

在 `pdf_search_app` 的根目录下，运行：
```bash
docker-compose up -d
```

运行后，您可以通过以下地址访问这些服务：
- **OpenSearch 仪表盘**: `http://localhost:5601`
- **MinIO 控制台**: `http://localhost:9001` (使用 `docker-compose.yml` 中配置的 `minioadmin` / `minioadmin` 登录)

### 第 2 步：运行 Flask 后端

1.  **导航到后端目录**：
    ```bash
    cd backend
    ```

2.  **创建虚拟环境并安装依赖**：
    ```bash
    # 创建一个虚拟环境
    uv venv
    # 激活它 (Windows)
    .\venv\Scripts\activate
    # (macOS/Linux)
    # source venv/bin/activate

    # 安装依赖
    uv pip install -r requirements.txt
    ```

3.  **启动 Flask 服务器**：
    **重要提示**：请使用 `uv run  app.py` 命令来启动，以确保初始化代码（如创建 MinIO 存储桶）能够被执行。
    ```bash
    uv run app.py
    ```
    后端服务器将在 `http://localhost:5001` 上启动。首次运行时，它会自动创建所需的 MinIO 存储桶 (`pdfs`) 和 OpenSearch 索引 (`pdf_documents`)。

### 第 3 步：运行 React 前端

1.  **打开一个新的终端**。

2.  **导航到前端目录**：
    ```bash
    cd frontend
    ```

3.  **安装依赖并启动开发服务器**：
    ```bash
    npm install
    npm start
    ```

4.  您的浏览器应该会自动打开 `http://localhost:3000`，在这里您会看到 PDF 上传界面。

---

## 工作原理

1.  **上传**: 您在 React 前端选择一个 PDF 文件并点击“上传”。
2.  **API 调用**: 前端将文件发送到 Flask 后端的 `/api/upload` 端点。
3.  **处理**: Flask 服务器执行以下操作：
    a.  将原始 PDF 文件直接上传到 **MinIO** 的 `pdfs` 存储桶中。
    b.  使用 `PyPDF2` 库从 PDF 中提取所有文本。
    c.  创建一个包含文件名、其在 MinIO 中的路径以及提取出的文本的 JSON 文档。
    d.  将此 JSON 文档索引到 **OpenSearch** 中。
4.  **结果**: 您现在可以访问 OpenSearch 仪表盘 (`http://localhost:5601`)，查看 `pdf_documents` 索引，并搜索您上传的 PDF 的内容。