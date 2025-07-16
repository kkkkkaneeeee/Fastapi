
# FastAPI LLM Business Assessment Backend

本项目为企业评估问卷的后端服务，基于 FastAPI，支持用户报告保存与 LLM 智能建议生成。前端可通过标准 RESTful API 与本服务对接。

---

## 目录

- [环境要求](#环境要求)
- [依赖安装](#依赖安装)
- [环境变量配置](#环境变量配置)
- [启动服务](#启动服务)
- [接口说明](#接口说明)
  - [1. 保存用户报告](#1-保存用户报告)
  - [2. 获取LLM建议](#2-获取llm建议)
- [常见问题](#常见问题)
- [开发建议](#开发建议)
- [联系方式](#联系方式)

---

## 环境要求

- Python 3.9 及以上
- pip

---

## 依赖安装

```bash
pip install -r requirements.txt
```

---

## 环境变量配置

请在项目根目录下新建 `.env` 文件，内容如下（根据实际情况填写）：

```env
AZURE_OPENAI_API_KEY=你的AzureOpenAI密钥
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=你的部署名
COSMOS_ENDPOINT=https://xxx.documents.azure.com:443/
COSMOS_KEY=你的CosmosDB密钥
```

---

## 启动服务

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- 启动后可通过 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 访问自动生成的接口文档（Swagger UI）。

---

## 接口说明

### 1. 保存用户报告

- **接口地址**：`POST /api/save-user-report`
- **请求头**：`Content-Type: application/json`
- **请求体示例**：

  ```json
  {
    "serviceOffering": { ... },
    "Base camp for success (go to market GTM)": { ... },
    "Tracking the climb (Performance Metrics PM)": { ... },
    "Scaling essentials (Commercial Essentials CE)": { ... },
    "Streamlining the climb (Optimal Processes OP)": { ... },
    "Assembling the team (People, Structure & Culture PSC)": { ... },
    "Toolbox for success (Systems & Tools ST)": { ... }
  }
  ```

- **响应示例**：

  ```json
  {
    "status": "success",
    "message": "Report saved successfully",
    "timestamp": "2025-07-14T16:23:51.513536"
  }
  ```

---

### 2. 获取LLM建议

- **接口地址**：`POST /api/llm-advice`
- **请求头**：`Content-Type: application/json`
- **请求体示例**：

  ```json
  {
    "userId": "user_default",
    "assessmentData": {
      "serviceOffering": { ... },
      "Base camp for success (go to market GTM)": { ... },
      "Tracking the climb (Performance Metrics PM)": { ... },
      "Scaling essentials (Commercial Essentials CE)": { ... },
      "Streamlining the climb (Optimal Processes OP)": { ... },
      "Assembling the team (People, Structure & Culture PSC)": { ... },
      "Toolbox for success (Systems & Tools ST)": { ... }
    }
  }
  ```

- **响应示例**：

  ```json
  {
    "advice": "Based on your assessment results, I provide the following business recommendations: ...",
    "timestamp": "2025-07-14T16:23:51.513536",
    "confidence_score": 0.85
  }
  ```

---

## 常见问题

### 1. CORS 跨域问题

- 后端已默认允许 `http://localhost:3000` 前端访问，如需更改请在 `main.py` 修改 `allow_origins`。

### 2. 422 Unprocessable Entity

- 检查请求体结构是否与接口文档一致，尤其是 `assessmentData` 必须为分组嵌套结构，且包含 `serviceOffering` 字段。

### 3. 500 Internal Server Error

- 检查环境变量、数据库连接、OpenAI Key 是否正确。
- 检查请求体内容是否完整。

### 4. 404 Not Found

- 检查请求的接口路径和端口是否正确，前端应请求 `http://localhost:8000/api/xxx`。

---

## 开发建议

- 推荐用 [Swagger UI](http://localhost:8000/docs) 或 Postman 测试接口。
- 前端开发时建议用全路径（如 `http://localhost:8000/api/llm-advice`）避免代理问题。
- 保证 assessmentData 结构与后端模型一致，避免 422 错误。

