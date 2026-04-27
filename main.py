from functools import lru_cache
import re
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from classifier import QuestionClassifier
from rag_service import RAGService


app = FastAPI(
    title="CloudSupport AI",
    description="FastAPI backend for technical support RAG assistant.",
    version="0.1.0",
)


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


STATUS_CODE_KNOWLEDGE: dict[int, dict[str, Any]] = {
    400: {
        "type": "bad_request",
        "explanation": "请求参数、请求体格式或 Header 不符合服务端要求。",
        "causes": ["参数缺失或类型错误", "JSON 格式不合法", "签名字段或 Header 缺失"],
        "steps": ["核对 API 文档中的必填字段", "检查 Content-Type 和请求体格式", "保留 request_id 便于服务端查询"],
    },
    401: {
        "type": "auth_failed",
        "explanation": "请求未通过身份认证。",
        "causes": ["Token 过期或无效", "AccessKey/SecretKey 错误", "鉴权 Header 未传递"],
        "steps": ["重新生成或刷新 Token", "检查 AK/SK 和签名算法", "确认请求时间没有明显偏差"],
    },
    403: {
        "type": "permission_denied",
        "explanation": "认证通过，但当前身份没有访问该资源或操作的权限。",
        "causes": ["账号权限不足", "资源策略限制", "IP 白名单或安全策略拦截"],
        "steps": ["检查 RAM/IAM 权限策略", "确认资源归属账号和地域", "检查安全组、白名单和访问控制策略"],
    },
    404: {
        "type": "not_found",
        "explanation": "请求路径、资源 ID 或路由不存在。",
        "causes": ["URL 路径错误", "资源已删除或地域不匹配", "服务未配置对应路由"],
        "steps": ["确认接口路径和 HTTP 方法", "检查资源 ID、地域和环境", "访问 /docs 确认后端实际暴露的接口"],
    },
    429: {
        "type": "rate_limited",
        "explanation": "请求触发限流或配额限制。",
        "causes": ["QPS 超过限制", "并发过高", "账号额度或模型调用配额不足"],
        "steps": ["降低重试频率并加入指数退避", "查看配额和限流策略", "申请扩容或拆分流量"],
    },
    500: {
        "type": "server_error",
        "explanation": "服务端内部错误。",
        "causes": ["应用异常", "依赖服务异常", "配置或环境变量缺失"],
        "steps": ["查看服务端日志和异常堆栈", "按 request_id 查询链路日志", "检查数据库、缓存、LLM API 等依赖状态"],
    },
    502: {
        "type": "upstream_error",
        "explanation": "网关或代理从上游服务收到了无效响应。",
        "causes": ["源站服务不可用", "上游连接被拒绝或重置", "负载均衡后端不健康", "HTTPS 回源握手失败"],
        "steps": ["检查源站进程、端口和健康检查", "确认网关到上游网络连通性", "核对回源协议、Host、SNI 和证书配置"],
    },
    504: {
        "type": "gateway_timeout",
        "explanation": "网关或代理等待上游服务响应超时。",
        "causes": ["源站响应慢", "上游网络超时", "数据库或第三方依赖耗时高", "代理超时时间过短"],
        "steps": ["对比 request_time 和 upstream_response_time", "检查应用慢日志和依赖服务耗时", "评估网关、CDN、负载均衡超时配置"],
    },
    499: {
        "type": "client_abort",
        "explanation": "客户端在服务端返回响应前主动断开连接，常见于 Nginx 日志。",
        "causes": ["客户端超时", "用户取消请求", "弱网或代理中断", "服务端响应慢导致客户端放弃等待"],
        "steps": ["检查客户端超时设置", "分析服务端请求耗时", "按地域、运营商、客户端版本聚合 499 分布"],
    },
}


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    """Create the RAG service once and reuse Chroma/LLM clients."""
    return RAGService()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="cloudsupport-ai", version="0.1.0")


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Answer a technical support question through the RAG pipeline."""
    try:
        result = get_rag_service().answer(payload.question)
        return ChatResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/ticket-triage", response_model=TicketTriageResponse)
def ticket_triage(payload: TicketTriageRequest) -> TicketTriageResponse:
    """Classify and route a cloud support ticket using stable rules."""
    text = f"{payload.title}\n{payload.description}\n{payload.affected_product or ''}"
    category = QuestionClassifier().classify(text).value
    status_codes = _extract_status_codes(text)
    keywords = _matched_keywords(text)
    priority = _infer_priority(text, status_codes, payload.customer_level)
    intent = _infer_intent(text)

    return TicketTriageResponse(
        category=category,
        priority=priority,
        intent=intent,
        assigned_team=_assigned_team(category),
        reason=f"根据标题和描述中的关键词命中 {category} 场景，优先级按影响范围、状态码和客户等级规则评估。",
        keywords=keywords,
        missing_info=_missing_info_for_support(text, category),
        next_actions=_next_actions_for_category(category, status_codes),
        confidence=0.78 if keywords else 0.55,
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

    return ApiDebugResponse(
        problem_type=knowledge["type"] if knowledge else _infer_problem_from_text(text),
        status_code_explanation=(
            f"{status_code}: {knowledge['explanation']}"
            if status_code and knowledge
            else "未提供明确状态码，请结合错误信息和服务端日志继续定位。"
        ),
        likely_causes=knowledge["causes"] if knowledge else _generic_api_causes(text),
        troubleshooting_steps=knowledge["steps"] if knowledge else _generic_api_steps(),
        required_info=_required_debug_info(payload),
        severity=_severity_from_status(status_code),
        confidence=0.82 if knowledge else 0.58,
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
            or "未识别到明确状态码，建议补充完整访问日志、应用日志和 request_id。"
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
    category = QuestionClassifier().classify(text).value
    status_codes = _extract_status_codes(text)
    actions = _next_actions_for_category(category, status_codes)
    missing_info = _missing_info_for_support(text, category)
    greeting = f"{payload.customer_name}，您好" if payload.customer_name else "您好"

    reply = (
        f"{greeting}：\n\n"
        f"我们已收到您反馈的“{payload.ticket_title}”问题。根据当前描述，问题初步归类为"
        f"「{category}」场景。\n\n"
        "初步建议如下：\n"
        + "\n".join(f"{index}. {action}" for index, action in enumerate(actions, start=1))
        + "\n\n为便于进一步定位，请补充：\n"
        + "\n".join(f"- {item}" for item in missing_info)
        + "\n\n收到补充信息后，我们可以继续协助您缩小故障链路并给出更具体的处理方案。"
    )

    return TicketReplyResponse(
        subject=f"关于「{payload.ticket_title}」的初步排查建议",
        reply=reply,
        action_items=actions,
        need_customer_confirm=missing_info,
        tone="professional",
        confidence=0.76,
    )


def _extract_status_codes(text: str) -> list[int]:
    codes: list[int] = []
    for candidate in re.findall(r"(?<!\d)([1-5]\d{2})(?!\d)", text):
        code = int(candidate)
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
    ]
    return [keyword for keyword in keywords if keyword.lower() in lowered]


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
        "CDN": "边缘网络/CDN 支持团队",
        "DNS": "域名解析/DNS 支持团队",
        "HTTPS": "证书与安全接入支持团队",
        "视频播放": "音视频技术支持团队",
        "Kubernetes": "容器云/Kubernetes 支持团队",
    }
    return mapping.get(category, "云产品技术支持一线团队")


def _next_actions_for_category(category: str, status_codes: list[int]) -> list[str]:
    if status_codes:
        code = status_codes[0]
        if code in STATUS_CODE_KNOWLEDGE:
            return STATUS_CODE_KNOWLEDGE[code]["steps"]

    mapping = {
        "CDN": ["确认访问 URL、加速域名和源站地址", "检查缓存命中率、回源状态和边缘节点日志", "对比直连源站与 CDN 访问结果"],
        "DNS": ["使用 dig/nslookup 检查解析结果", "确认 CNAME、A 记录和 TTL 配置", "检查权威 DNS 与本地递归 DNS 是否一致"],
        "HTTPS": ["检查证书有效期、证书链和域名匹配", "确认 TLS 版本和加密套件兼容性", "核对 CDN/负载均衡的 HTTPS 回源配置"],
        "视频播放": ["确认播放 URL、格式和播放器错误码", "检查首帧耗时、卡顿时间点和码率", "对比不同地域、网络和终端的播放表现"],
        "Kubernetes": ["查看 Pod 事件、重启次数和容器日志", "检查 Deployment、Service、Ingress 配置", "确认资源配额、探针和节点状态"],
    }
    return mapping.get(category, ["补充 request_id、时间范围和完整错误信息", "确认问题影响范围和复现步骤", "检查相关服务日志与监控指标"])


def _missing_info_for_support(text: str, category: str) -> list[str]:
    missing = []
    if "request" not in text.lower() and "trace" not in text.lower():
        missing.append("request_id 或 trace_id")
    if not re.search(r"\d{4}-\d{2}-\d{2}|\d{2}:\d{2}", text):
        missing.append("问题发生时间和持续时间")
    if category in {"CDN", "DNS", "HTTPS", "视频播放"} and "http" not in text.lower():
        missing.append("受影响 URL、域名或播放地址")
    if category == "Kubernetes" and "namespace" not in text.lower():
        missing.append("集群、namespace、Pod 名称和相关 kubectl describe/logs 输出")
    return missing or ["当前信息较完整，可继续提供日志和监控截图以提高定位准确度"]


def _required_debug_info(payload: ApiDebugRequest) -> list[str]:
    required = []
    if not payload.request_id:
        required.append("request_id / trace_id")
    if not payload.status_code:
        required.append("HTTP 状态码")
    if not payload.url:
        required.append("完整请求 URL")
    if not payload.response_body:
        required.append("响应体或错误响应片段")
    return required or ["当前 API 调试信息较完整"]


def _missing_info_for_logs(log_text: str) -> list[str]:
    missing = []
    lowered = log_text.lower()
    if "request" not in lowered and "trace" not in lowered:
        missing.append("request_id / trace_id")
    if "upstream" not in lowered:
        missing.append("upstream_response_time / upstream_addr")
    if not re.search(r"\d{4}-\d{2}-\d{2}|\d{2}:\d{2}", log_text):
        missing.append("日志时间范围")
    return missing or ["当前日志字段较完整"]


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
    if problem == "timeout":
        return ["客户端或网关超时", "服务端处理耗时过长", "上游依赖响应慢"]
    if problem == "auth_failed":
        return ["Token 或签名无效", "鉴权 Header 缺失", "账号权限或时间戳异常"]
    if problem == "rate_limited":
        return ["请求频率超过限制", "并发过高", "账号或模型调用额度不足"]
    return ["请求参数或路径不匹配", "服务端依赖异常", "缺少 request_id，无法精确查询链路"]


def _generic_api_steps() -> list[str]:
    return ["保留完整 URL、Method、Header、Body 和响应体", "使用 request_id 查询服务端链路日志", "对比成功请求和失败请求的参数差异"]


def _generic_log_causes(log_text: str) -> list[str]:
    problem = _infer_problem_from_text(log_text)
    if problem == "timeout":
        return ["请求链路存在超时", "上游服务响应慢", "网络链路不稳定"]
    if problem == "dns_resolution":
        return ["DNS 解析失败或解析结果不一致", "本地递归 DNS 缓存异常", "域名记录配置不完整"]
    return ["日志证据不足", "需要结合访问日志、应用日志和监控指标继续判断"]


def _generic_log_steps() -> list[str]:
    return ["补充完整日志时间范围和 request_id", "检查应用错误日志、网关日志和上游依赖日志", "对比正常请求与异常请求的状态码、耗时和来源地域"]


def _severity_from_status(status_code: int | None) -> str:
    if status_code in {500, 502, 504}:
        return "high"
    if status_code in {401, 403, 429, 499}:
        return "medium"
    if status_code and status_code >= 400:
        return "low"
    return "unknown"
