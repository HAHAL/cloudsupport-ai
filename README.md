# CloudSupport AI：企业知识库 AI 技术支持助手

CloudSupport AI 是一个面向企业技术支持、SaaS 产品支持、AI 应用支持和知识库问答场景的智能支持助手。项目基于 FastAPI、RAG、Prompt Engineering、Markdown 知识库和规则兜底能力，支持知识库问答、工单分诊、API 报错分析、日志分析、客户回复生成、升级信息收集和回答反馈记录。

项目提供 Web 控制台、Swagger API 文档、Docker 部署和 GitHub Actions CI/CD 流程。默认不依赖外部大模型 API Key，未配置模型服务时也可以通过规则兜底完成主要流程验证；配置 OpenAI、通义千问或兼容 OpenAI 协议的模型服务后，可以启用更完整的 RAG 知识库回答。

## 项目简介

CloudSupport AI 将企业支持工作中的常见动作抽象为可复用的工作流：理解客户问题、分类工单、分析 API 错误、解析日志、生成客户回复、整理升级信息，并通过反馈记录持续改进知识库和 Prompt。

它适用于以下场景：

- 企业技术支持团队处理客户问题。
- SaaS 产品支持团队分析登录、权限、接口和页面异常。
- AI 应用支持团队排查 LLM API、RAG 检索和 Prompt 输出问题。
- 应用运维团队分析 5xx、超时、反向代理和部署异常。
- 内部知识库问答与支持流程标准化。

## 项目背景

在企业技术支持场景中，常见问题包括接口报错、登录失败、权限异常、服务不可用、上游超时、客户描述不完整、知识库检索效率低等。传统处理方式依赖人工经验，容易出现排查步骤不统一、客户回复不规范、升级信息缺失等问题。

CloudSupport AI 尝试将技术支持流程标准化，通过规则兜底、知识库检索和可选大模型生成能力，帮助支持人员快速完成问题初判、排查建议生成、客户回复和升级摘要整理。

## 核心功能

| 功能模块 | 说明 | 示例场景 |
|---|---|---|
| 企业知识库问答 | 基于 Markdown 知识库返回排查建议、参考来源和需要补充的信息。 | RAG 回答不准确如何排查。 |
| API 报错分析 | 分析 `400`、`401`、`403`、`404`、`408`、`429`、`500`、`502`、`503`、`504` 等状态码。 | API 返回 `429 Too Many Requests`。 |
| 日志分析 | 提取 `status`、`request_time`、`upstream_response_time`、`request_id`、`error` 等字段。 | `504 upstream timed out`。 |
| 工单分诊 | 根据问题标题、描述、客户等级、影响范围判断问题类型和优先级。 | 客户登录系统时报 `403`。 |
| 客户回复生成 | 生成专业、克制、可复制到工单中的回复草稿。 | 针对权限异常收集账号、时间、request ID 和截图。 |
| 升级信息收集 | 输出升级摘要、缺失信息、建议负责人和临时处理建议。 | 需要转研发、运维或平台团队。 |
| 回答反馈 | 记录 `useful` / `not_useful` 反馈。 | 用于后续优化知识库和 Prompt。 |
| Web 控制台 | 提供可视化操作入口。 | 部署后直接在浏览器中完成完整流程验证。 |
| Swagger 文档 | 提供接口调试和 API 验证入口。 | 访问 `/docs` 调试接口。 |
| CI/CD 流程 | 基于 GitHub Actions 完成依赖安装、语法检查、健康检查、Docker 构建和服务器部署。 | 代码提交后自动执行 CI，手动触发 Deploy 发布到服务器。 |

## 技术架构

```text
User / Support Engineer
        ↓
Web Console / Swagger
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

核心设计：

- FastAPI 负责 API 路由、Swagger 文档和 Web 控制台入口。
- RAG Service 负责知识库文档加载、切分、检索和回答生成。
- Rule Engine 在没有模型 Key 时提供稳定的兜底分析。
- Prompt Templates 约束输出结构、诊断字段和客户回复风格。
- Feedback JSONL 记录回答质量反馈，便于后续优化知识库和规则。
- Docker Compose 负责本地和服务器部署。
- GitHub Actions 负责基础 CI 检查和手动部署流程。

## 技术栈

| 类型 | 技术 |
|---|---|
| 后端框架 | Python, FastAPI, Pydantic |
| AI 应用 | LangChain, RAG, Prompt Engineering |
| 知识库 | Markdown, TXT, PDF, Chroma |
| 前端页面 | HTML, CSS, JavaScript |
| 部署 | Docker, Docker Compose |
| 自动化 | GitHub Actions |
| 接口调试 | Swagger, Postman, curl |
| 反馈记录 | JSONL 本地文件 |

## 项目结构

```text
cloudsupport-ai/
├── main.py
├── app/
├── static/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── knowledge/
│   ├── api/
│   ├── web-app/
│   ├── deployment/
│   ├── ai-support/
│   └── support-process/
├── examples/
├── postman/
├── docs/
│   ├── images/
│   └── videos/
├── scripts/
│   ├── deploy.sh
│   └── health_check.sh
├── data/
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/
│   ├── ci.yml
│   └── deploy.yml
├── requirements.txt
├── .env.example
├── README.md
└── README_EN.md
```

说明：当前后端保持轻量结构，核心服务文件位于项目根目录；`app/` 目录为后续模块化拆分预留。Web 控制台位于 `static/`。

## Web 控制台

启动服务后访问：

```text
http://localhost:8000/
```

Web 控制台支持：

- 企业知识库问答
- 知识库状态、版本列表、文档切分预览和检索测试
- 工单分诊
- API 报错分析
- 日志分析
- 客户回复生成
- 升级信息收集
- `useful` / `not_useful` 反馈提交

结果区域默认展示结构化诊断报告卡片，包含问题摘要、可能原因、排查步骤、需要补充的信息、客户回复建议和升级条件。原始 JSON 保留为调试信息，默认折叠。

## API 接口

Swagger / OpenAPI 文档地址：

```text
http://localhost:8000/docs
```

| API | Method | 说明 |
|---|---|---|
| `/health` | GET | 服务健康检查 |
| `/chat` | POST | 企业知识库问答 |
| `/ticket-triage` | POST | 工单分诊 |
| `/api-debug` | POST | API 报错分析 |
| `/log-analyze` | POST | HTTP / 应用日志分析 |
| `/ticket-reply` | POST | 客户回复草稿生成 |
| `/escalation-summary` | POST | 升级信息收集 |
| `/feedback` | POST | 回答反馈记录 |
| `/knowledge/status` | GET | 查看知识库状态 |
| `/knowledge/versions` | GET | 查看文档版本 |
| `/knowledge/reindex` | POST | 重建知识库索引 |
| `/knowledge/search` | POST | 检索知识库 |
| `/knowledge/preview-chunks` | POST | 预览文档切分结果 |
| `/knowledge/deprecate` | POST | 标记文档版本为 deprecated |
| `/docs` | GET | Swagger API 文档 |

兼容接口：`POST /escalation-info` 仍可使用，便于旧客户端平滑迁移；新接入建议使用 `/escalation-summary`。

### API 示例

企业知识库问答：

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "企业知识库问答结果不准确，应该如何排查？"
  }'
```

工单分诊：

```bash
curl -X POST http://localhost:8000/ticket-triage \
  -H "Content-Type: application/json" \
  -d '{
    "title": "客户反馈登录系统时报 403",
    "description": "客户使用企业账号登录后台时提示 Forbidden，影响部分用户访问。",
    "customer_level": "enterprise",
    "affected_product": "SaaS Platform"
  }'
```

API 报错分析：

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

日志分析：

```bash
curl -X POST http://localhost:8000/log-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "log_text": "status=504 request_time=60.001 upstream_response_time=60.000 error=\"upstream timed out\" request_id=req_504_demo",
    "question": "为什么接口返回 504？"
  }'
```

知识库检索测试：

```bash
curl -X POST http://localhost:8000/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "企业知识库问答结果不准确，应该如何排查？",
    "top_k": 4,
    "include_deprecated": false
  }'
```

## 知识库结构

推荐将企业知识库整理为以下通用结构：

```text
knowledge/
├── api/
│   ├── authentication-errors.md
│   ├── permission-errors.md
│   ├── rate-limit-errors.md
│   ├── timeout-errors.md
│   └── status-code-troubleshooting.md
├── web-app/
│   ├── login-failure.md
│   ├── page-slow.md
│   ├── service-unavailable.md
│   └── cors-issue.md
├── deployment/
│   ├── docker-deploy-troubleshooting.md
│   ├── nginx-reverse-proxy.md
│   └── database-connection-error.md
├── ai-support/
│   ├── rag-retrieval-quality.md
│   ├── prompt-optimization.md
│   ├── hallucination-control.md
│   └── llm-api-errors.md
└── support-process/
    ├── ticket-triage.md
    ├── customer-reply-template.md
    └── escalation-checklist.md
```

当前仓库保留了部分历史知识库文件，可逐步迁移到上述通用目录。推荐优先沉淀：

- API 鉴权、权限、限流、超时和状态码排查。
- Web 应用登录失败、页面慢、服务不可用和跨域问题。
- Docker 部署、反向代理和数据库连接异常。
- AI 应用中的 RAG 检索质量、Prompt 优化、幻觉控制和 LLM API 错误。
- 工单分诊、客户回复模板和升级检查清单。

## 知识库与 RAG 流程

CloudSupport AI 的知识库基于本地 Markdown、TXT 和 PDF 文件。系统支持文档加载、YAML Front Matter 元数据解析、文档切分、检索测试和可选 Chroma 向量索引。

默认情况下，如果没有配置外部 Embedding 或 LLM Key，系统使用关键词 fallback 检索，仍可完成知识库问答、切分预览和参考来源返回。配置外部 Embedding Provider 后，可将知识库文档切分后写入 Chroma，启用 Top-K 相似度检索。

```text
Knowledge Files
        ↓
Metadata Parsing
        ↓
Recursive Chunk Split
        ↓
Keyword Fallback / Chroma Vector Search
        ↓
Prompt Context Assembly
        ↓
Structured Answer + References
```

## 知识库版本管理

Markdown 文档可以通过 YAML Front Matter 管理知识元数据，包括 `doc_id`、`version`、`status`、`effective_from`、`deprecated_at` 和 `tags`。文档切分后，每个 chunk 会继承这些 metadata，并额外生成 `chunk_id`、`chunk_index`、`content_hash` 和 `document_hash`，用于检索结果展示、内容变更判断和后续增量索引扩展。

元数据示例：

```markdown
---
doc_id: api-rate-limit-errors
title: API 限流错误排查
version: v1.2.0
status: active
owner: support-team
effective_from: 2026-05-01
deprecated_at:
tags:
  - api
  - rate-limit
  - 429
---
```

如果文档没有 Front Matter，系统会根据文件路径生成默认 metadata：`doc_id` 来自路径，`title` 使用文件名，`version` 默认为 `v1.0.0`，`status` 默认为 `active`，`owner` 默认为 `unknown`，`tags` 根据目录推断。

## 新旧知识处理策略

- 新知识使用 `status=active`，默认参与检索和问答。
- 旧知识使用 `status=deprecated`，默认不参与检索，仅在 `include_deprecated=true` 时返回，并在结果中明确显示状态。
- 草稿知识使用 `status=draft`，默认不参与检索和 reindex，只在版本列表中展示。
- `/chat`、`/knowledge/search` 和 `/knowledge/reindex` 默认只使用 active 文档，避免旧知识污染回答。
- `document_hash` 用于判断整篇文档变化，`content_hash` 用于判断 chunk 内容变化。
- 当前实现以轻量级全量重建和本地状态覆盖为主，后续可扩展为增量索引、版本回滚和审批发布流程。

## 文档切分参数

| 环境变量 | 默认值 | 说明 |
|---|---|---|
| `CHUNK_SIZE` | `800` | 单个 chunk 的目标长度 |
| `CHUNK_OVERLAP` | `120` | 相邻 chunk 的重叠长度 |
| `RAG_TOP_K` | `4` | 默认检索返回数量 |
| `CHROMA_DIR` | `chroma_data` | Chroma 本地存储目录 |
| `CHROMA_COLLECTION` | `cloudsupport_kb` | Chroma collection 名称 |

## 知识库管理接口

| 接口 | 方法 | 说明 |
|---|---|---|
| `/knowledge/status` | GET | 查看知识库状态、切分参数、向量库目录和当前检索模式 |
| `/knowledge/versions` | GET | 查看所有文档版本、状态和文档 Hash |
| `/knowledge/reindex` | POST | 重新加载文档、切分 active 文档，并在 provider ready 时写入 Chroma |
| `/knowledge/search` | POST | 测试知识库检索效果，默认只检索 active 文档 |
| `/knowledge/preview-chunks` | POST | 按文本或知识库文件路径预览切分结果 |
| `/knowledge/deprecate` | POST | 通过本地版本覆盖记录将文档版本标记为 deprecated |

## 快速开始

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

健康检查：

```bash
curl -f http://127.0.0.1:8000/health
```

## Docker 部署

启动服务：

```bash
docker compose up --build -d
```

查看状态和日志：

```bash
docker compose ps
docker compose logs -f
```

健康检查：

```bash
curl -f http://127.0.0.1:8000/health
```

停止服务：

```bash
docker compose down
```

Docker Compose 默认映射端口 `8000:8000`，并挂载：

- `./knowledge:/app/knowledge`
- `./chroma_data:/app/chroma_data`
- `./data:/app/data`

其中 `data/` 用于保存反馈 JSONL 等运行时数据，不提交到仓库。

## 环境变量

规则兜底接口和 Web 控制台不需要外部模型 Key。完整 RAG 回答可按需配置模型服务：

```env
LLM_PROVIDER=rule
EMBEDDING_PROVIDER=local
OPENAI_API_KEY=
DASHSCOPE_API_KEY=

CHUNK_SIZE=800
CHUNK_OVERLAP=120
RAG_TOP_K=4
CHROMA_DIR=chroma_data
CHROMA_COLLECTION=cloudsupport_kb

# 如需启用外部模型服务，可按需配置：
# LLM_PROVIDER=openai
# EMBEDDING_PROVIDER=openai
# OPENAI_API_KEY=your_openai_key
```

默认无 Key 模式走 `keyword_fallback`。配置 Embedding Provider 后，知识库可写入 Chroma 并启用向量检索。不要将真实 API Key 或 `.env` 文件提交到仓库。建议通过服务器环境变量、本地 `.env` 或 GitHub Actions Secrets 配置敏感信息。

## CI/CD 流程

项目提供轻量级 GitHub Actions 流程，用于基础检查、Docker 镜像构建、服务器部署和健康检查。

### CI 阶段

触发条件：

- push 到 `main`
- pull_request 到 `main`

执行内容：

1. Checkout 代码。
2. 安装 Python 依赖。
3. 执行 Python 语法检查。
4. 运行最小接口测试 `PYTHONPATH=. pytest -q`。
5. 启动 FastAPI 服务。
6. 调用 `/health` 健康检查，失败时输出 `app.log`。
7. 构建 Docker 镜像。

### CD 阶段

Deploy workflow 通过 GitHub Actions 手动触发：

1. 通过 SSH 登录服务器。
2. 进入服务器项目目录。
3. 执行 `git pull`。
4. 如 `.env` 不存在，则从 `.env.example` 复制。
5. 使用 Docker Compose 重新构建和启动服务。
6. 通过 `/health` 重试验证部署状态。

部署健康检查最多重试 30 次，每次间隔 3 秒。如果服务仍未就绪，Deploy workflow 会输出最近 100 行容器日志并返回失败状态。

需要配置的 GitHub Secrets：

| Secret | 说明 |
|---|---|
| `SERVER_HOST` | 服务器 IP 或域名 |
| `SERVER_USER` | SSH 登录用户名 |
| `SERVER_SSH_KEY` | 用于登录服务器的 SSH 私钥内容 |
| `SERVER_PORT` | SSH 端口，通常为 `22` |
| `PROJECT_DIR` | 服务器上的项目目录，例如 `/opt/cloudsupport-ai` |

本地部署脚本：

```bash
chmod +x scripts/*.sh
./scripts/deploy.sh
```

健康检查脚本：

```bash
./scripts/health_check.sh
HEALTH_URL=http://127.0.0.1:8000/health ./scripts/health_check.sh
MAX_RETRIES=30 SLEEP_SECONDS=3 ./scripts/health_check.sh
```

## 操作演示流程

1. 打开 Web 控制台。
2. 打开 Swagger 文档。
3. 查看 `/health` 健康检查。
4. 演示 API 429 报错分析。
5. 演示日志 504 分析。
6. 演示登录 403 工单分诊。
7. 演示客户回复生成。
8. 演示知识库问答。
9. 查看知识库状态。
10. 查看文档版本列表。
11. 预览文档切分结果。
12. 测试知识库检索。
13. 勾选 `include_deprecated` 对比历史知识。
14. 重建知识库索引。
15. 再进行知识库问答。
16. 演示升级信息收集。
17. 提交 `useful` / `not_useful` 反馈。
18. 查看 GitHub Actions CI/CD 流程。

## 项目截图

### Web 控制台首页

![Web 控制台首页](docs/images/web-console-home.png)

### API 报错分析结果

![API 报错分析结果](docs/images/api-debug-result.png)

### 日志分析结果

![日志分析结果](docs/images/log-analyze-result.png)

### 工单分诊结果

![工单分诊结果](docs/images/ticket-triage-result.png)

### CI Success

![CI Success](docs/images/ci-success.png)

### Deploy Success

![Deploy Success](docs/images/deploy-success.png)

可继续补充：

- 知识库状态
- 文档切分预览
- 知识库检索测试

## 操作演示视频

视频文件路径：

```text
docs/videos/cloudsupport-ai-demo.mp4
```

待补充。

## 安全说明

- 不要把服务器密码、SSH 私钥、API Key 或 `.env` 文件提交到仓库。
- GitHub Actions 部署所需信息通过 Secrets 配置。
- 反馈文件、向量库数据和运行时数据默认写入本地目录，并通过 `.gitignore` 忽略。
- 接入实际业务前，建议补充认证鉴权、角色权限、审计日志、数据脱敏、访问控制和监控告警。

## 后续优化方向

- 接入企业工单系统和客户支持台。
- 支持多知识库与多租户隔离。
- 增加用户登录、角色权限和访问审计。
- 增加 RAG 评测集和回答质量评分。
- 支持反馈驱动的知识库更新流程。
- 支持对话历史和工单上下文记忆。
- 增加知识库管理页面。
- 增加更完善的日志、指标和告警能力。
