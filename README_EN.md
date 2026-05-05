# CloudSupport AI: Enterprise Knowledge Base AI Support Assistant

CloudSupport AI is a lightweight AI-assisted support assistant for enterprise technical support, SaaS product support, AI application support, knowledge base Q&A, API error analysis, log analysis, ticket triage, customer reply drafting, escalation information collection, and answer feedback tracking.

The project can run without an external LLM API key. Rule-based fallback workflows are available by default. When OpenAI, Qwen, or another OpenAI-compatible provider is configured, the `/chat` endpoint can use a fuller RAG workflow.

## Overview

CloudSupport AI helps support engineers understand customer issues faster and convert repeated support patterns into structured, reusable workflows. It provides both a Web Console and Swagger API documentation for visual operation and API debugging.

## Key Features

1. Knowledge Base Q&A
2. Ticket Triage
3. API Error Analysis
4. HTTP and Application Log Analysis
5. Customer Reply Drafting
6. Escalation Information Collection
7. Answer Feedback Tracking
8. Static Web Console
9. Dockerized Deployment

## Architecture

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

## Tech Stack

- Python
- FastAPI
- Pydantic
- Markdown Knowledge Base
- LangChain
- Chroma
- Prompt Templates
- Rule-based Fallback
- HTML / CSS / JavaScript Web Console
- Docker Compose
- Postman

## Quick Start

```bash
git clone https://github.com/HAHAL/cloudsupport-ai.git
cd cloudsupport-ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open:

```text
Web Console: http://localhost:8000/
Swagger:     http://localhost:8000/docs
```

Docker:

```bash
docker compose up --build -d
```

## API Endpoints

| API | Method | Purpose |
| --- | --- | --- |
| `/health` | GET | Service health check |
| `/chat` | POST | Knowledge base Q&A |
| `/ticket-triage` | POST | Ticket classification and routing |
| `/api-debug` | POST | API error troubleshooting |
| `/log-analyze` | POST | HTTP and application log analysis |
| `/ticket-reply` | POST | Customer reply draft generation |
| `/escalation-info` | POST | Escalation information collection |
| `/feedback` | POST | Answer feedback tracking |
| `/docs` | GET | Swagger API documentation |

## Environment Variables

Rule-based workflows do not require external credentials. Full RAG behavior can be enabled with a configured model provider:

```env
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your_openai_key

# Or Qwen / DashScope OpenAI-compatible endpoint
# LLM_PROVIDER=qwen
# EMBEDDING_PROVIDER=qwen
# DASHSCOPE_API_KEY=your_dashscope_key
```

Never commit real API keys to the repository.

## Knowledge Base

The Markdown knowledge base covers CDN, DNS, HTTPS, video streaming, Kubernetes, LLM API errors, rate limit, timeout, authentication failures, RAG retrieval quality, prompt optimization, and Function Calling schema issues.

## Feedback

The `/feedback` endpoint stores `useful` and `not_useful` labels in local JSONL format:

```text
feedback/answer_feedback.jsonl
```

This file is ignored by Git and can be used to improve rules, prompts, and knowledge base content.

## Limitations

CloudSupport AI is a technical support workflow prototype. It does not connect to real customer data, ticket systems, or production monitoring systems by default. Before using it in a business environment, add authentication, authorization, audit logs, data masking, monitoring, evaluation datasets, and persistent storage.

## Roadmap

- Connect to enterprise ticket systems
- Add multi-tenant knowledge base isolation
- Add authentication and role-based access control
- Add observability metrics
- Add RAG answer evaluation
- Add feedback-driven knowledge base updates
- Add conversation history and ticket context memory
