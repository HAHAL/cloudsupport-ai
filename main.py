from datetime import datetime, timezone
from functools import lru_cache
import json
import re
from pathlib import Path
from typing import Any
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from classifier import QuestionClassifier
from rag_service import RAGService


app = FastAPI(
    title="CloudSupport AI",
    description="Enterprise knowledge base AI technical support assistant.",
    version="0.1.0",
)

FEEDBACK_FILE = Path("feedback/answer_feedback.jsonl")


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, description="用户的技术支持问题")


class Reference(BaseModel):
    source: str
    category: str
    score: float | None = None
    page: int | None = None
    content_preview: str


class RetrievedContent(BaseModel):
    content: str
    source: str
    category: str
    score: float | None = None
    page: int | None = None


class ChatResponse(BaseModel):
    question: str
    category: str
    answer: str
    retrieved_contents: list[RetrievedContent]
    references: list[Reference]
    metadata: dict


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class TicketTriageRequest(BaseModel):
    title: str = Field(..., min_length=2, description="工单标题")
    description: str = Field(..., min_length=2, description="工单描述")
    customer_level: str | None = Field(None, description="客户等级，例如 free/vip/enterprise")
    affected_product: str | None = Field(None, description="用户填写的受影响产品")


class TicketTriageResponse(BaseModel):
    category: str
    priority: str
    intent: str
    assigned_team: str
    reason: str
    keywords: list[str]
    missing_info: list[str]
    next_actions: list[str]
    confidence: float
    impact_scope: str
    required_info: list[str]
    suggested_owner: str


class ApiDebugRequest(BaseModel):
    method: str | None = Field(None, description="HTTP 方法，例如 GET/POST")
    url: str | None = Field(None, description="请求 URL")
    status_code: int | None = Field(None, ge=100, le=599, description="HTTP 状态码")
    error_message: str | None = Field(None, description="错误信息")
    request_id: str | None = Field(None, description="请求 ID / Trace ID")
    response_body: str | None = Field(None, description="响应体或错误响应片段")


class ApiDebugResponse(BaseModel):
    problem_type: str
    status_code_explanation: str
    likely_causes: list[str]
    troubleshooting_steps: list[str]
    required_info: list[str]
    severity: str
    confidence: float
    issue_summary: str
    possible_causes: list[str]
    required_customer_info: list[str]
    temporary_workaround: list[str]
    escalation_needed: bool


class LogAnalyzeRequest(BaseModel):
    log_text: str = Field(..., min_length=2, description="HTTP 响应、Nginx 日志或应用日志")
    question: str | None = Field(None, description="希望重点分析的问题")


class LogAnalyzeResponse(BaseModel):
    problem_type: str
    status_code_explanation: str
    problem_causes: list[str]
    troubleshooting_suggestions: list[str]
    detected_status_codes: list[int]
    evidence: list[str]
    missing_info: list[str]
    confidence: float


class TicketReplyRequest(BaseModel):
    ticket_title: str = Field(..., min_length=2, description="工单标题")
    ticket_description: str = Field(..., min_length=2, description="工单描述")
    analysis_context: str | None = Field(None, description="已有排查结论或日志摘要")
    customer_name: str | None = Field(None, description="客户名称")


class TicketReplyResponse(BaseModel):
    subject: str
    reply: str
    action_items: list[str]
    need_customer_confirm: list[str]
    tone: str
    confidence: float
    customer_reply: str
    internal_notes: list[str]
    next_actions: list[str]
    escalation_condition: list[str]


class EscalationInfoRequest(BaseModel):
    issue_summary: str = Field(..., min_length=2, description="Brief issue summary")
    product_area: str | None = Field(None, description="Product area, such as CDN, LLM, DNS, Video, Kubernetes")
    observed_error: str | None = Field(None, description="Observed error message, status code, or log snippet")
    business_impact: str | None = Field(None, description="Impact scope and urgency")


class EscalationInfoResponse(BaseModel):
    category: str
    escalation_team: str
    required_information: list[str]
    suggested_summary: str
    escalation_criteria: list[str]
    confidence: float


class FeedbackRequest(BaseModel):
    workflow: str = Field(..., min_length=2, description="Workflow name, such as chat/api-debug/log-analyze")
    rating: Literal["useful", "not_useful"] = Field(..., description="Feedback label")
    question: str | None = Field(None, description="Original user question or ticket summary")
    answer: str | None = Field(None, description="Answer or response draft to be reviewed")
    comment: str | None = Field(None, description="Optional feedback comment")
    source: str | None = Field("web-console", description="Feedback source")


class FeedbackResponse(BaseModel):
    status: str
    saved: bool
    feedback_file: str
    received_at: str


STATUS_CODE_KNOWLEDGE: dict[int, dict[str, Any]] = {
    400: {
        "type": "bad_request",
        "explanation": "400 Bad Request means the request parameters, body, or headers do not match the API contract.",
        "causes": ["Missing or invalid parameters", "Invalid JSON payload", "Model name, message format, or context length is invalid"],
        "steps": ["Compare the request with the API documentation", "Verify model name, Content-Type, JSON format, and required fields", "Check context length, message format, and max_tokens settings"],
    },
    401: {
        "type": "auth_failed",
        "explanation": "401 Unauthorized means the request did not pass authentication.",
        "causes": ["Invalid or expired API key/token", "Incorrect AccessKey/SecretKey or signature", "Authorization header is missing or malformed"],
        "steps": ["Verify that the API key is loaded in the runtime environment", "Check the model or endpoint permission for the key", "Confirm the base URL, timestamp, and signature algorithm"],
    },
    403: {
        "type": "permission_denied",
        "explanation": "403 Forbidden means the identity is authenticated but not authorized for the requested resource or operation.",
        "causes": ["Insufficient IAM/RAM permission", "Resource policy restriction", "IP allowlist, firewall, or access-control policy blocked the request"],
        "steps": ["Check IAM/RAM policies and workspace permissions", "Confirm the resource owner, region, and project", "Review allowlist, security group, and access-control rules"],
    },
    404: {
        "type": "not_found",
        "explanation": "404 Not Found means the route, resource ID, or API path cannot be found.",
        "causes": ["Incorrect URL path or HTTP method", "Resource does not exist or belongs to another region", "The backend service does not expose the requested route"],
        "steps": ["Verify the API path and method", "Check resource ID, region, and environment", "Use /docs to confirm available backend endpoints"],
    },
    429: {
        "type": "rate_limited",
        "explanation": "429 Too Many Requests means the request hit a rate limit, quota limit, or concurrency limit.",
        "causes": ["RPM/TPM/QPS limit exceeded", "Concurrent requests are too high", "Workspace quota, billing, or model entitlement is insufficient"],
        "steps": ["Add retry with exponential backoff and jitter", "Check RPM/TPM/QPS, quota, and billing status", "Reduce concurrency or request a quota increase"],
    },
    408: {
        "type": "request_timeout",
        "explanation": "408 Request Timeout means the client or gateway timed out before the request completed.",
        "causes": ["Request body is too large", "Network path is slow or unstable", "Client timeout is shorter than model inference time"],
        "steps": ["Reduce prompt size and max output tokens", "Check client, proxy, and gateway timeout settings", "Compare streaming and non-streaming behavior"],
    },
    500: {
        "type": "server_error",
        "explanation": "500 Internal Server Error means the backend encountered an unexpected error.",
        "causes": ["Application exception", "Dependency failure", "Missing runtime configuration or environment variable"],
        "steps": ["Check backend logs and exception stack traces", "Use request ID to query service-side traces", "Verify database, cache, gateway, and LLM API dependencies"],
    },
    502: {
        "type": "upstream_error",
        "explanation": "502 Bad Gateway means the gateway or CDN received an invalid response from the origin or upstream service.",
        "causes": ["Origin service is unavailable", "Upstream connection was refused or reset", "Load balancer backend is unhealthy", "HTTPS back-to-origin handshake failed"],
        "steps": ["Check origin process, listening port, and health check status", "Verify CDN or gateway connectivity to the origin", "Review origin protocol, Host header, SNI, and certificate configuration"],
    },
    504: {
        "type": "gateway_timeout",
        "explanation": "504 Gateway Timeout means the CDN, gateway, or load balancer timed out while waiting for the origin response.",
        "causes": ["Origin response latency is high", "Upstream network timeout or packet loss", "Database/cache/third-party dependency is slow", "Gateway or CDN timeout is shorter than origin processing time"],
        "steps": ["Compare request_time and upstream_response_time", "Check application slow logs and dependency latency", "Verify origin connectivity and evaluate CDN/gateway timeout settings"],
    },
    503: {
        "type": "service_unavailable",
        "explanation": "503 Service Unavailable means the upstream model service or gateway is temporarily unavailable.",
        "causes": ["Temporary model service unavailability", "Gateway or upstream overload", "Regional service instability"],
        "steps": ["Retry with exponential backoff", "Compare other models or regions if available", "Collect request ID, timestamp, model name, and response body for escalation"],
    },
    499: {
        "type": "client_abort",
        "explanation": "499 Client Closed Request means the client closed the connection before the server returned a response, commonly seen in Nginx logs.",
        "causes": ["Client-side timeout", "User or client canceled the request", "Weak network or proxy interruption", "Server response was too slow and the client gave up"],
        "steps": ["Compare client timeout with request_time and upstream_response_time", "Check client SDK/browser logs", "Aggregate 499 errors by region, ISP, and client version"],
    },
}


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    """Create the RAG service once and reuse retrieval or model clients."""
    return RAGService()


@app.get("/", include_in_schema=False)
def web_console() -> FileResponse:
    return FileResponse("index.html")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="cloudsupport-ai", version="0.1.0")


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Answer an enterprise support question through RAG or deterministic fallback."""
    try:
        result = get_rag_service().answer(payload.question)
        return ChatResponse(**result)
    except Exception:
        category = _infer_support_category(payload.question)
        status_codes = _extract_status_codes(payload.question)
        actions = _next_actions_for_category(category, status_codes)
        missing_info = _missing_info_for_support(payload.question, category)
        answer = _build_fallback_chat_answer(category, status_codes, actions, missing_info)
        return ChatResponse(
            question=payload.question,
            category=category,
            answer=answer,
            retrieved_contents=[],
            references=[],
            metadata={
                "mode": "rule_based_fallback",
                "has_context": False,
                "reason": "RAG provider is not configured or temporarily unavailable",
            },
        )


@app.post("/ticket-triage", response_model=TicketTriageResponse)
def ticket_triage(payload: TicketTriageRequest) -> TicketTriageResponse:
    """Classify and route a cloud support ticket using stable rules."""
    text = f"{payload.title}\n{payload.description}\n{payload.affected_product or ''}"
    category = _infer_support_category(text)
    status_codes = _extract_status_codes(text)
    keywords = _matched_keywords(text)
    priority = _infer_priority(text, status_codes, payload.customer_level)
    intent = _infer_intent(text)

    return TicketTriageResponse(
        category=category,
        priority=priority,
        intent=intent,
        assigned_team=_assigned_team(category),
        reason=_triage_reason(category, keywords, status_codes, priority),
        keywords=keywords,
        missing_info=_missing_info_for_support(text, category),
        next_actions=_next_actions_for_category(category, status_codes),
        confidence=0.78 if keywords else 0.55,
        impact_scope=_impact_scope(text, priority),
        required_info=_missing_info_for_support(text, category),
        suggested_owner=_assigned_team(category),
    )


@app.post("/api-debug", response_model=ApiDebugResponse)
def api_debug(payload: ApiDebugRequest) -> ApiDebugResponse:
    """Diagnose API call failures with status-code and message rules."""
    text = " ".join(
        item
        for item in [
            payload.method,
            payload.url,
            payload.error_message,
            payload.response_body,
            payload.request_id,
        ]
        if item
    )
    status_code = payload.status_code or _first_status_code(text)
    knowledge = STATUS_CODE_KNOWLEDGE.get(status_code or 0)
    likely_causes = knowledge["causes"] if knowledge else _generic_api_causes(text)
    troubleshooting_steps = knowledge["steps"] if knowledge else _generic_api_steps()
    required_info = _required_debug_info(payload)

    return ApiDebugResponse(
        problem_type=knowledge["type"] if knowledge else _infer_problem_from_text(text),
        status_code_explanation=(
            f"{status_code}: {knowledge['explanation']}"
            if status_code and knowledge
            else "No explicit HTTP status code was provided. Continue the investigation with the error message, request ID, and server-side logs."
        ),
        likely_causes=likely_causes,
        troubleshooting_steps=troubleshooting_steps,
        required_info=required_info,
        severity=_severity_from_status(status_code),
        confidence=0.82 if knowledge else 0.58,
        issue_summary=_api_issue_summary(payload, status_code),
        possible_causes=likely_causes,
        required_customer_info=required_info,
        temporary_workaround=_temporary_workaround(status_code, text),
        escalation_needed=_escalation_needed_for_api(status_code, text),
    )


@app.post("/log-analyze", response_model=LogAnalyzeResponse)
def log_analyze(payload: LogAnalyzeRequest) -> LogAnalyzeResponse:
    """Analyze HTTP/log text with deterministic fallback rules."""
    status_codes = _extract_status_codes(payload.log_text)
    primary_code = status_codes[0] if status_codes else None
    knowledge = STATUS_CODE_KNOWLEDGE.get(primary_code or 0)

    return LogAnalyzeResponse(
        problem_type=knowledge["type"] if knowledge else _infer_problem_from_text(payload.log_text),
        status_code_explanation=(
            "；".join(
                f"{code}: {STATUS_CODE_KNOWLEDGE[code]['explanation']}"
                for code in status_codes
                if code in STATUS_CODE_KNOWLEDGE
            )
            or "No explicit HTTP status code was detected. Please provide complete access logs, application logs, and request ID for further analysis."
        ),
        problem_causes=knowledge["causes"] if knowledge else _generic_log_causes(payload.log_text),
        troubleshooting_suggestions=knowledge["steps"] if knowledge else _generic_log_steps(),
        detected_status_codes=status_codes,
        evidence=_extract_evidence(payload.log_text),
        missing_info=_missing_info_for_logs(payload.log_text),
        confidence=0.84 if knowledge else 0.6,
    )


@app.post("/ticket-reply", response_model=TicketReplyResponse)
def ticket_reply(payload: TicketReplyRequest) -> TicketReplyResponse:
    """Generate a professional support-ticket reply with rule-based content."""
    text = f"{payload.ticket_title}\n{payload.ticket_description}\n{payload.analysis_context or ''}"
    category = _infer_support_category(text)
    status_codes = _extract_status_codes(text)
    actions = _next_actions_for_category(category, status_codes)
    missing_info = _missing_info_for_support(text, category)
    greeting = f"Dear {payload.customer_name}," if payload.customer_name else "Dear Customer,"

    reply = "\n\n".join(
        [
            greeting,
            "Thank you for contacting us.",
            (
                f"Based on the information provided, this issue appears to be related to "
                f"{category}. We are not making a final conclusion yet, and the next step is "
                "to collect the evidence required to narrow down the affected layer."
            ),
            "Initial troubleshooting suggestions:\n"
            + "\n".join(f"{index}. {action}" for index, action in enumerate(actions, start=1)),
            "To continue the investigation, could you please provide the following information:\n"
            + "\n".join(f"{index}. {item}" for index, item in enumerate(missing_info, start=1)),
            (
                "Once we receive the above information, we will continue the analysis and "
                "provide the next update with more specific findings or escalation guidance."
            ),
            "Best regards,\nTechnical Support Team",
        ]
    )

    return TicketReplyResponse(
        subject=f"Initial troubleshooting request for: {payload.ticket_title}",
        reply=reply,
        action_items=actions,
        need_customer_confirm=missing_info,
        tone="professional",
        confidence=0.76,
        customer_reply=reply,
        internal_notes=[
            f"Detected support category: {category}",
            "Do not confirm the root cause until request IDs, timestamps, raw errors, and reproduction evidence are reviewed.",
            "Use the required information list to drive the next customer update.",
        ],
        next_actions=actions,
        escalation_condition=_escalation_criteria(category, status_codes),
    )


@app.post("/escalation-info", response_model=EscalationInfoResponse)
def escalation_info(payload: EscalationInfoRequest) -> EscalationInfoResponse:
    """Collect information required before escalating a support issue."""
    text = "\n".join(
        item
        for item in [
            payload.issue_summary,
            payload.product_area,
            payload.observed_error,
            payload.business_impact,
        ]
        if item
    )
    category = _infer_support_category(text)
    status_codes = _extract_status_codes(text)

    return EscalationInfoResponse(
        category=category,
        escalation_team=_escalation_team(category),
        required_information=_missing_info_for_support(text, category),
        suggested_summary=_build_escalation_summary(payload, category, status_codes),
        escalation_criteria=_escalation_criteria(category, status_codes),
        confidence=0.78 if payload.observed_error or status_codes else 0.58,
    )


@app.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    """Save answer feedback locally for knowledge base and prompt improvement."""
    received_at = datetime.now(timezone.utc).isoformat()
    record = {
        "received_at": received_at,
        "workflow": payload.workflow,
        "rating": payload.rating,
        "question": payload.question,
        "answer": payload.answer,
        "comment": payload.comment,
        "source": payload.source,
    }

    try:
        FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
        with FEEDBACK_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {exc}") from exc

    return FeedbackResponse(
        status="ok",
        saved=True,
        feedback_file=str(FEEDBACK_FILE),
        received_at=received_at,
    )


def _extract_status_codes(text: str) -> list[int]:
    codes: list[int] = []
    for match in re.findall(r"(?<!\d)([1-5]\d{2})(?!\d)", text):
        code = int(match)
        if code not in codes:
            codes.append(code)
    return codes


def _first_status_code(text: str) -> int | None:
    codes = _extract_status_codes(text)
    return codes[0] if codes else None


def _matched_keywords(text: str) -> list[str]:
    lowered = text.lower()
    keywords = [
        "cdn",
        "dns",
        "https",
        "ssl",
        "证书",
        "视频",
        "播放",
        "k8s",
        "kubernetes",
        "pod",
        "超时",
        "timeout",
        "502",
        "504",
        "499",
        "鉴权",
        "限流",
        "rate limit",
        "quota",
        "function calling",
        "schema",
        "rag",
        "embedding",
    ]
    return [keyword for keyword in keywords if keyword.lower() in lowered]


def _infer_support_category(text: str) -> str:
    lowered = text.lower()
    if any(
        keyword in lowered
        for keyword in [
            "llm",
            "large language model",
            "model endpoint",
            "chat/completions",
            "function calling",
            "tool calling",
            "prompt",
            "rag",
            "embedding",
            "token",
            "rate limit",
            "quota",
        ]
    ):
        return "LLM"
    return QuestionClassifier().classify(text).value


def _infer_priority(text: str, status_codes: list[int], customer_level: str | None) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["全站", "大面积", "不可用", "p0", "紧急"]):
        return "p0"
    if any(code in status_codes for code in [500, 502, 504]) or customer_level in {
        "vip",
        "enterprise",
    }:
        return "p1"
    if any(word in lowered for word in ["失败", "异常", "卡顿", "超时", "timeout"]):
        return "p2"
    return "p3"


def _infer_intent(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["怎么配置", "如何配置", "配置"]):
        return "configuration"
    if any(word in lowered for word in ["报错", "失败", "异常", "超时", "timeout", "不可用"]):
        return "troubleshooting"
    if any(word in lowered for word in ["账单", "费用", "计费"]):
        return "billing"
    if any(word in lowered for word in ["bug", "缺陷"]):
        return "bug"
    return "consulting"


def _assigned_team(category: str) -> str:
    mapping = {
        "CDN": "Edge Network / CDN Support Team",
        "DNS": "DNS and Traffic Management Support Team",
        "HTTPS": "TLS / Security Support Team",
        "视频播放": "Media Delivery / Video Support Team",
        "Kubernetes": "Cloud Native / Kubernetes Support Team",
        "LLM": "LLM API Support Team",
    }
    return mapping.get(category, "Cloud Support Team")


def _escalation_team(category: str) -> str:
    mapping = {
        "CDN": "Edge Network / CDN Support Team",
        "DNS": "DNS and Traffic Management Support Team",
        "HTTPS": "TLS / Security Support Team",
        "视频播放": "Media Delivery / Video Support Team",
        "Kubernetes": "Cloud Native / Kubernetes Support Team",
        "LLM": "LLM API Support Team",
    }
    return mapping.get(category, "Product Engineering Team")


def _triage_reason(
    category: str,
    keywords: list[str],
    status_codes: list[int],
    priority: str,
) -> str:
    keyword_text = ", ".join(keywords[:6]) if keywords else "general support signals"
    status_text = ", ".join(str(code) for code in status_codes) if status_codes else "no explicit HTTP status code"
    return (
        f"The ticket matches {category} support signals such as {keyword_text}. "
        f"Detected status information: {status_text}. Based on the reported impact and "
        f"available evidence, it is currently classified as priority {priority}. "
        "The first response should focus on evidence collection, reproduction scope, "
        "and identifying whether the issue is on the client, edge, origin, or LLM API layer."
    )


def _impact_scope(text: str, priority: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["all users", "global", "全站", "大面积"]):
        return "broad impact"
    if any(word in lowered for word in ["enterprise", "paid users", "checkout", "payment", "production"]):
        return "business-critical path"
    if priority in {"p0", "p1"}:
        return "high priority impact, scope requires confirmation"
    return "limited or unknown impact"


def _next_actions_for_category(category: str, status_codes: list[int]) -> list[str]:
    if status_codes:
        code = status_codes[0]
        if code in STATUS_CODE_KNOWLEDGE:
            return STATUS_CODE_KNOWLEDGE[code]["steps"]

    mapping = {
        "CDN": ["Confirm the affected domain, full URL, and origin address", "Check cache status, origin status, edge logs, and back-to-origin latency", "Compare CDN access with direct origin access from the same region"],
        "DNS": ["Run dig/nslookup against multiple recursive resolvers", "Verify CNAME/A/AAAA records, TTL, and authoritative DNS configuration", "Compare authoritative DNS results with client-side DNS results"],
        "HTTPS": ["Check certificate validity, SAN/CN match, and certificate chain", "Verify TLS version, cipher compatibility, SNI, and Host header", "Compare certificate deployment on CDN, load balancer, and origin"],
        "视频播放": ["Collect playback URL, player error code, SDK version, and client region", "Break down DNS, TCP, TLS, TTFB, manifest, and first segment download time", "Compare first-frame time across regions, ISPs, devices, and bitrates"],
        "Kubernetes": ["Check Pod events, restart count, and container logs", "Review Deployment, Service, Ingress, requests/limits, and scheduling constraints", "Verify ResourceQuota, node status, taints, tolerations, and PVC binding"],
        "LLM": ["Confirm the model name, endpoint, workspace, and SDK version", "Collect request ID, response body, token usage, and rate-limit headers", "Check API key permission, quota, billing status, and retry/backoff configuration"],
    }
    return mapping.get(category, ["Collect request ID, timestamp with timezone, and complete error response", "Confirm reproduction steps, affected region, and business impact", "Review application logs, gateway logs, and monitoring metrics"])


def _missing_info_for_support(text: str, category: str) -> list[str]:
    missing = []
    if "request" not in text.lower() and "trace" not in text.lower():
        missing.append("request ID or trace ID")
    if not re.search(r"\d{4}-\d{2}-\d{2}|\d{2}:\d{2}", text):
        missing.append("timestamp with timezone and issue duration")
    if category in {"CDN", "DNS", "HTTPS", "视频播放"} and "http" not in text.lower():
        missing.append("affected domain, full URL, or playback URL")
    if category == "Kubernetes" and "namespace" not in text.lower():
        missing.append("cluster ID, namespace, Pod name, kubectl describe output, and container logs")
    if category == "LLM" and "request" not in text.lower():
        missing.append("LLM request body with sensitive values removed")
    if category == "LLM" and "model" not in text.lower():
        missing.append("model name, endpoint, SDK version, and workspace or project scope")
    if "region" not in text.lower() and "ip" not in text.lower():
        missing.append("client region or source IP")
    if "impact" not in text.lower() and "影响" not in text.lower():
        missing.append("business impact and affected user scope")
    return missing or ["The provided information is sufficient for initial triage; logs and monitoring screenshots can further improve analysis quality"]


def _required_debug_info(payload: ApiDebugRequest) -> list[str]:
    required = []
    if not payload.request_id:
        required.append("request_id / trace_id")
    if not payload.status_code:
        required.append("HTTP status code")
    if not payload.url:
        required.append("full request URL")
    if not payload.response_body:
        required.append("response body or error response snippet")
    return required or ["The current API debugging information is sufficient for initial analysis"]


def _missing_info_for_logs(log_text: str) -> list[str]:
    missing = []
    lowered = log_text.lower()
    if "request" not in lowered and "trace" not in lowered:
        missing.append("request_id / trace_id")
    if "upstream" not in lowered:
        missing.append("upstream_response_time / upstream_addr")
    if not re.search(r"\d{4}-\d{2}-\d{2}|\d{2}:\d{2}", log_text):
        missing.append("log timestamp and timezone")
    if "region" not in lowered and "ip" not in lowered:
        missing.append("client region or source IP")
    return missing or ["The log fields are sufficient for initial analysis"]


def _extract_evidence(log_text: str) -> list[str]:
    lines = [line.strip() for line in log_text.splitlines() if line.strip()]
    evidence = [
        line[:240]
        for line in lines
        if re.search(r"(?<!\d)([1-5]\d{2})(?!\d)|error|timeout|failed|exception", line, re.I)
    ]
    return evidence[:5] or lines[:3]


def _infer_problem_from_text(text: str) -> str:
    lowered = text.lower()
    if "context_length_exceeded" in lowered or "context length" in lowered:
        return "context_length_exceeded"
    if "stream interrupted" in lowered or "connection reset" in lowered:
        return "stream_interrupted"
    if "timeout" in lowered or "超时" in lowered:
        return "timeout"
    if "auth" in lowered or "unauthorized" in lowered or "鉴权" in lowered:
        return "auth_failed"
    if "rate" in lowered or "limit" in lowered or "限流" in lowered:
        return "rate_limited"
    if "dns" in lowered or "解析" in lowered:
        return "dns_resolution"
    return "unknown"


def _generic_api_causes(text: str) -> list[str]:
    problem = _infer_problem_from_text(text)
    if problem == "context_length_exceeded":
        return ["Prompt, chat history, or RAG context exceeds the model context window", "Top-K or chunk size may be too large", "max_tokens may leave insufficient room for input"]
    if problem == "stream_interrupted":
        return ["Streaming connection was interrupted by client, proxy, or gateway", "Read timeout is too short", "Output length or inference time is too high for the current connection"]
    if problem == "timeout":
        return ["Client or gateway timeout", "Backend processing latency is too high", "Upstream dependency is slow or unstable"]
    if problem == "auth_failed":
        return ["Invalid token or signature", "Authorization header is missing", "Account permission or timestamp is invalid"]
    if problem == "rate_limited":
        return ["Request rate exceeds the limit", "Concurrency is too high", "Account quota, billing, or model entitlement is insufficient"]
    return ["Request path or parameters do not match the API contract", "Backend dependency may be unavailable", "Missing request ID makes trace lookup difficult"]


def _generic_api_steps() -> list[str]:
    return ["Keep the full URL, method, headers, request body, and response body", "Use request ID to query backend trace logs", "Compare parameters between successful and failed requests"]


def _api_issue_summary(payload: ApiDebugRequest, status_code: int | None) -> str:
    method = payload.method or "unknown method"
    url = payload.url or "unknown endpoint"
    status = status_code or "unknown status"
    message = payload.error_message or payload.response_body or "no error message provided"
    return f"{method} {url} returned {status}. Observed error: {message}"


def _temporary_workaround(status_code: int | None, text: str) -> list[str]:
    problem = _infer_problem_from_text(text)
    if problem == "context_length_exceeded":
        return ["Reduce chat history, RAG Top-K, chunk size, or max output tokens", "Summarize long context before sending it to the model"]
    if problem == "stream_interrupted":
        return ["Increase client read timeout and check proxy buffering", "Reduce max output tokens or switch to non-streaming mode for comparison"]
    if status_code == 401:
        return ["Regenerate or rotate the API key", "Verify environment variable loading and endpoint permission with a minimal request"]
    if status_code == 403:
        return ["Use an account or workspace with the required model permission", "Check region, allowlist, and security policy before retrying"]
    if status_code == 400:
        return ["Reduce the request to a minimal valid payload", "Validate model name, message format, and context length before retrying"]
    if status_code == 429 or problem == "rate_limited":
        return ["Apply exponential backoff with jitter", "Reduce concurrency and token usage while checking quota or billing status"]
    if status_code in {408, 504} or problem == "timeout":
        return ["Reduce prompt size or max output tokens", "Increase client timeout where appropriate and retry non-idempotent operations carefully"]
    if status_code and status_code >= 500:
        return ["Retry with exponential backoff", "Fail over to a fallback model or endpoint if available"]
    return ["Collect request evidence and retry with a minimal reproducible request"]


def _escalation_needed_for_api(status_code: int | None, text: str) -> bool:
    lowered = text.lower()
    if status_code in {500, 502, 503, 504}:
        return True
    if status_code in {401, 403, 429} and "request" in lowered:
        return True
    return any(keyword in lowered for keyword in ["persistent", "reproducible", "stream interrupted", "context_length_exceeded"])


def _generic_log_causes(log_text: str) -> list[str]:
    problem = _infer_problem_from_text(log_text)
    if problem == "timeout":
        return ["The request path contains a timeout", "Upstream service latency is high", "Network path may be unstable"]
    if problem == "dns_resolution":
        return ["DNS resolution failed or returned inconsistent results", "Recursive DNS cache may be stale", "DNS record configuration may be incomplete"]
    return ["The current log evidence is insufficient", "Access logs, application logs, and monitoring metrics are needed for further analysis"]


def _generic_log_steps() -> list[str]:
    return ["Provide the full log time range and request ID", "Check application error logs, gateway logs, and upstream dependency logs", "Compare status code, latency, and client region between successful and failed requests"]


def _build_escalation_summary(
    payload: EscalationInfoRequest,
    category: str,
    status_codes: list[int],
) -> str:
    status_text = ", ".join(str(code) for code in status_codes) if status_codes else "not provided"
    impact = payload.business_impact or "impact scope not provided"
    return (
        f"Category: {category}. Issue summary: {payload.issue_summary}. "
        f"Observed status/error: {payload.observed_error or status_text}. "
        f"Business impact: {impact}. Additional evidence should be collected before escalation."
    )


def _escalation_criteria(category: str, status_codes: list[int]) -> list[str]:
    if any(code in status_codes for code in [500, 502, 503, 504]):
        return [
            "The issue affects multiple users, regions, or critical business paths",
            "Origin, gateway, or LLM provider errors persist after basic configuration checks",
            "Request ID and timestamp are available for backend trace lookup",
        ]
    if category == "LLM":
        return [
            "API key, quota, endpoint, and model permission have been verified",
            "The same request fails consistently with request ID available",
            "Schema, prompt, or RAG behavior differs from expected API behavior",
        ]
    return [
        "The issue is reproducible with clear timestamps and request evidence",
        "Basic configuration checks have been completed",
        "The support team needs product-side trace, configuration, or service health confirmation",
    ]


def _severity_from_status(status_code: int | None) -> str:
    if status_code in {500, 502, 504}:
        return "high"
    if status_code in {401, 403, 429, 499}:
        return "medium"
    if status_code and status_code >= 400:
        return "low"
    return "unknown"


def _build_fallback_chat_answer(
    category: str,
    status_codes: list[int],
    actions: list[str],
    missing_info: list[str],
) -> str:
    status_text = ", ".join(str(code) for code in status_codes) if status_codes else "not detected"
    return "\n".join(
        [
            f"问题类型初步判断：{category}",
            f"检测到的状态码：{status_text}",
            "",
            "初步排查建议：",
            *[f"{index}. {action}" for index, action in enumerate(actions, start=1)],
            "",
            "建议补充信息：",
            *[f"{index}. {item}" for index, item in enumerate(missing_info, start=1)],
            "",
            "说明：当前回答由规则兜底生成。配置 LLM 与 Embedding API Key 后，/chat 可启用更完整的知识库检索与模型回答。",
        ]
    )
