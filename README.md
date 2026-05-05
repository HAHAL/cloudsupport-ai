# CloudSupport AI：企业知识库 AI 技术支持助手

CloudSupport AI 是一个面向企业技术支持、SaaS 产品支持和 AI 应用交付场景的智能支持助手。项目基于 FastAPI、RAG、Prompt Engineering、Markdown 知识库和规则兜底能力，支持知识库问答、工单分诊、API 报错分析、日志分析、客户回复生成、升级信息收集和回答反馈记录。

项目默认不依赖外部大模型 API Key。未配置模型服务时，系统仍可通过规则兜底能力完成主要工作流演示；配置 OpenAI、通义千问或兼容 OpenAI 协议的模型服务后，可以启用更完整的 RAG 知识库回答。

## 项目简介

CloudSupport AI 用于帮助技术支持人员快速理解客户问题，并把常见支持流程转化为结构化、可复用的 API 和 Web 控制台能力。它适用于企业知识库问答、SaaS 产品支持、AI 应用支持、API 错误分析、HTTP 日志分析、工单分诊、客户回复生成、升级信息收集和回答质量反馈。

项目目标：

- 帮助技术支持人员快速理解客户问题。
- 根据企业知识库生成标准化排查建议。
- 对 API 报错、日志片段、状态码异常进行初步分析。
- 生成专业、克制、可直接发给客户的回复草稿。
- 在需要升级时生成研发、运维或平台团队所需的信息清单。
- 沉淀支持流程，提升问题处理一致性。
- 通过 Web 控制台和 Swagger 同时支持可视化操作与接口调试。

## 核心功能

### 1. 知识库问答

- 支持基于 Markdown 文档的知识库检索。
- 支持用户输入自然语言问题。
- 返回问题判断、排查步骤、需要补充的信息和参考来源。
- 未配置外部模型 Key 时，返回本地规则兜底回答。

### 2. 工单分诊

- 根据客户问题标题、描述、客户等级、影响范围识别问题类型。
- 输出优先级、初步判断、下一步处理建议、建议负责人和 SLA 建议。
- 覆盖 CDN、DNS、HTTPS、视频播放、Kubernetes、LLM API 和通用云产品问题。

### 3. API 报错分析

- 支持 `400`、`401`、`403`、`404`、`408`、`429`、`500`、`502`、`503`、`504` 等常见状态码分析。
- 输出可能原因、排查步骤、客户需补充信息、临时处理建议和升级判断。
- 适用于 SaaS API、LLM API、网关 API 和后端服务接口排障。

### 4. 日志分析

- 支持输入 Nginx、应用日志、API 调用日志片段。
- 提取 `status`、`request_time`、`upstream_response_time`、`request_id`、`error` 等关键字段。
- 输出初步诊断建议、证据片段、缺失信息和后续排查方向。

### 5. 客户回复生成

- 根据问题背景和分析结论，生成专业、克制、可发送给客户的回复草稿。
- 输出客户回复、内部备注、下一步动作和升级条件。
- 避免在证据不足时直接下最终结论。

### 6. 升级信息收集

- 当问题需要升级到研发、运维或平台团队时，生成需要补充的信息清单。
- 输出升级摘要、建议负责人、升级条件和临时处理建议。
- 帮助减少缺少 request ID、时间戳、日志、复现步骤导致的重复沟通。

### 7. 回答反馈

- 支持对 AI 或规则回答进行 `useful` / `not_useful` 标记。
- 反馈保存到本地 JSONL 文件：`feedback/answer_feedback.jsonl`。
- 可用于后续优化知识库内容、Prompt 模板和规则兜底逻辑。

### 8. Web 控制台

- 提供轻量级可视化页面。
- 支持 API 报错分析、日志分析、工单分诊、客户回复生成、知识库问答、升级信息收集和反馈提交。
- 与 Swagger `/docs` 并存，便于操作演示和接口调试。

## 技术架构

- FastAPI：提供 RESTful API、Swagger 文档和 Web 控制台入口。
- Markdown Knowledge Base：维护产品文档、FAQ、故障手册和支持流程。
- RAG Pipeline：文档切分、检索、上下文拼接、回答生成。
- Prompt Templates：约束输出格式和回复风格。
- Rule-based Fallback：在没有配置 LLM Key 时，也可以演示规则分析能力。
- Static Web Console：通过 HTML、CSS、JavaScript 调用后端接口。
- Docker Compose：用于本地和服务器部署。

```text
User / Support Engineer
        ↓
Web Console / Swagger Docs
        ↓
FastAPI REST API
        ↓
Support Workflow Services
        ↓
Rule Engine + RAG Service + Prompt Templates
        ↓
Markdown Knowledge Base / Feedback JSONL
        ↓
Structured Diagnosis / Reply Draft / Escalation Summary
```

## Web 控制台

启动服务后访问：

```text
http://localhost:8000/
```

控制台包含以下工作流：

- 知识库问答
- 工单分诊
- API 报错分析
- 日志分析
- 客户回复生成
- 升级信息收集
- 回答反馈提交

## API 文档

Swagger / OpenAPI 文档地址：

```text
http://localhost:8000/docs
```

## API 接口

| API | Method | 说明 |
| --- | --- | --- |
| `/health` | GET | 服务健康检查 |
| `/chat` | POST | 企业知识库问答 |
| `/ticket-triage` | POST | 工单分诊 |
| `/api-debug` | POST | API 报错分析 |
| `/log-analyze` | POST | HTTP / 应用日志分析 |
| `/ticket-reply` | POST | 客户回复草稿生成 |
| `/escalation-info` | POST | 升级信息收集 |
| `/feedback` | POST | 回答反馈记录 |
| `/docs` | GET | Swagger API 文档 |

## 快速启动

### 本地启动

```bash
git clone https://github.com/HAHAL/cloudsupport-ai.git
cd cloudsupport-ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问：

```text
Web 控制台: http://localhost:8000/
Swagger:    http://localhost:8000/docs
```

### Docker 启动

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f
```

停止服务：

```bash
docker compose down
```

## 环境变量

规则兜底接口和 Web 控制台不需要外部模型 Key。完整 RAG 回答可按需配置模型服务：

```env
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your_openai_key

# 或使用通义千问 / DashScope OpenAI-compatible endpoint
# LLM_PROVIDER=qwen
# EMBEDDING_PROVIDER=qwen
# DASHSCOPE_API_KEY=your_dashscope_key
```

不要将真实 API Key 提交到仓库。建议通过服务器环境变量或本地 `.env` 文件配置。

## API 示例

### 知识库问答

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "LLM API 返回 429 Too Many Requests，应该如何排查？"
  }'
```

### 工单分诊

```bash
curl -X POST http://localhost:8000/ticket-triage \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Enterprise customer reports LLM API timeout",
    "description": "The customer reports intermittent timeout when calling chat/completions. The issue affects production workflow in Singapore region.",
    "customer_level": "enterprise",
    "affected_product": "LLM API"
  }'
```

### API 报错分析

```bash
curl -X POST http://localhost:8000/api-debug \
  -H "Content-Type: application/json" \
  -d '{
    "method": "POST",
    "url": "https://api.example.com/v1/chat/completions",
    "status_code": 429,
    "error_message": "Too Many Requests: rate limit exceeded for current workspace.",
    "request_id": "req_sample_20260505_001"
  }'
```

### 日志分析

```bash
curl -X POST http://localhost:8000/log-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "log_text": "2026-05-05T10:15:20+08:00 status=504 request_time=60.001 upstream_response_time=60.000 request_id=req_sample_001 error=\"upstream timed out\"",
    "question": "Why did this API request return 504?"
  }'
```

### 客户回复生成

```bash
curl -X POST http://localhost:8000/ticket-reply \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_title": "LLM API timeout during peak traffic",
    "ticket_description": "Customer reports timeout when calling the model endpoint.",
    "analysis_context": "Possible timeout or request-size issue. Need request ID, timestamp, model name, and retry behavior.",
    "customer_name": "Customer"
  }'
```

### 升级信息收集

```bash
curl -X POST http://localhost:8000/escalation-info \
  -H "Content-Type: application/json" \
  -d '{
    "issue_summary": "LLM API returns persistent 504 for production requests",
    "product_area": "LLM",
    "observed_error": "504 Gateway Timeout, request_id=req_sample_002",
    "business_impact": "Production workflow is delayed for multiple enterprise users."
  }'
```

### 回答反馈

```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": "api-debug",
    "rating": "useful",
    "question": "API returned 429",
    "answer": "Check rate limit, quota, retry policy and request volume.",
    "comment": "The troubleshooting steps are actionable."
  }'
```

## 知识库目录

```text
knowledge/
├── cdn/
├── dns/
├── https/
├── video/
├── kubernetes/
└── llm/
```

知识库内容覆盖：

- CDN 502 / 504、cache miss、high TTFB
- DNS resolution failure
- TLS certificate issue
- video first frame slow、HLS playback stutter
- Kubernetes Pod Pending
- LLM API 401 / 403 / 429 / 5xx / timeout
- Prompt optimization
- RAG retrieval quality
- Function Calling schema invalid

## 项目结构

```text
.
├── main.py
├── rag_service.py
├── prompt_manager.py
├── classifier.py
├── log_analyzer.py
├── index.html
├── knowledge/
├── docs/
├── examples/
├── postman/
├── eval/
├── TEST_RESULT.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── README_EN.md
```

## 设计说明

- 规则兜底优先保证可演示、可部署和接口稳定。
- RAG 用于把企业知识库中的排障流程与客户问题关联起来。
- Prompt 模板用于控制输出格式、回复语气和缺失信息收集。
- 反馈 JSONL 用于记录回答质量，便于后续改进知识库和规则。
- Web 控制台面向支持人员操作，Swagger 面向接口调试。

## 限制说明

CloudSupport AI 是一个技术支持工作流原型。默认不连接真实客户数据、真实工单系统或生产监控系统。部署到实际业务环境前，需要补充认证鉴权、权限控制、审计日志、数据脱敏、监控告警、评测集和持久化存储。

## 后续规划

- 接入真实工单系统和客户支持台。
- 支持多知识库与多租户隔离。
- 增加用户登录、角色权限和访问审计。
- 接入 Prometheus / Grafana 监控。
- 增加 RAG 回答质量评测集。
- 支持反馈驱动的知识库更新流程。
- 支持对话历史和工单上下文记忆。
- 增加更完整的 Web 控制台权限与配置页面。
