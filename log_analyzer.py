import json
import os
import re
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv is listed in requirements.txt. This keeps static imports
    # usable in minimal environments before dependencies are installed.
    pass


class LogAnalyzer:
    """Analyze HTTP responses or log text with an LLM.

    The analyzer first extracts common HTTP status codes and builds a small
    deterministic context. The LLM then uses that context plus the raw log text
    to produce structured JSON.
    """

    STATUS_CODE_KNOWLEDGE: dict[int, dict[str, Any]] = {
        502: {
            "name": "Bad Gateway",
            "explanation": "网关或代理从上游服务收到了无效响应。",
            "common_causes": [
                "源站或上游服务异常、进程退出或端口不可用",
                "代理到源站的连接被拒绝、连接重置或协议不匹配",
                "负载均衡后端实例不健康",
                "TLS/HTTPS 回源握手失败",
            ],
            "suggestions": [
                "检查源站服务进程、监听端口和健康检查状态",
                "检查代理/CDN/负载均衡到源站的连通性",
                "查看上游服务错误日志和网关错误日志",
                "确认回源协议、Host、SNI 和证书配置是否一致",
            ],
        },
        504: {
            "name": "Gateway Timeout",
            "explanation": "网关或代理等待上游服务响应超时。",
            "common_causes": [
                "源站响应慢或接口处理时间过长",
                "上游网络链路延迟、丢包或连接超时",
                "数据库、缓存或第三方依赖拖慢请求",
                "代理、CDN 或负载均衡超时时间配置过短",
            ],
            "suggestions": [
                "确认请求耗时和超时发生的具体链路位置",
                "检查源站慢日志、应用日志和依赖服务耗时",
                "排查网络连通性、丢包率和跨地域访问延迟",
                "根据业务 SLA 调整网关、CDN、负载均衡和应用超时配置",
            ],
        },
        499: {
            "name": "Client Closed Request",
            "explanation": "客户端在服务端返回响应前主动断开连接，常见于 Nginx 日志。",
            "common_causes": [
                "客户端、浏览器或移动端主动取消请求",
                "客户端侧超时设置短于服务端处理耗时",
                "网络切换、弱网或中间代理断开连接",
                "服务端响应慢导致客户端放弃等待",
            ],
            "suggestions": [
                "对比 request_time、upstream_response_time 和客户端超时设置",
                "检查客户端日志或 SDK 超时配置",
                "分析服务端慢请求和上游依赖耗时",
                "按地域、运营商、客户端版本聚合 499 请求分布",
            ],
        },
    }

    def __init__(self, llm: ChatOpenAI | None = None) -> None:
        self.llm = llm or self._build_llm()
        self.prompt = self._build_prompt()

    def analyze(self, log_text: str, question: str = "请分析这段日志") -> dict[str, Any]:
        """Analyze log text and return structured JSON.

        Returns:
            {
              "problem_type": str,
              "status_code_explanation": str,
              "problem_causes": list[str],
              "troubleshooting_suggestions": list[str],
              "detected_status_codes": list[int],
              "evidence": list[str],
              "confidence": float
            }
        """
        detected_status_codes = self.extract_status_codes(log_text)
        status_context = self._build_status_context(detected_status_codes)

        chain = self.prompt | self.llm
        response = chain.invoke(
            {
                "question": question,
                "log_text": log_text,
                "status_context": status_context,
                "detected_status_codes": detected_status_codes,
            }
        )

        return self._normalize_result(
            content=response.content,
            detected_status_codes=detected_status_codes,
        )

    @classmethod
    def extract_status_codes(cls, text: str) -> list[int]:
        """Extract HTTP status codes from raw response text or access logs."""
        candidates = re.findall(r"(?<!\d)([1-5]\d{2})(?!\d)", text)
        status_codes = []
        for candidate in candidates:
            code = int(candidate)
            if 100 <= code <= 599 and code not in status_codes:
                status_codes.append(code)
        return status_codes

    def _build_status_context(self, status_codes: list[int]) -> str:
        """Build deterministic status-code context for the LLM."""
        if not status_codes:
            return "未从日志中明确识别到 HTTP 状态码。"

        blocks = []
        for code in status_codes:
            knowledge = self.STATUS_CODE_KNOWLEDGE.get(code)
            if not knowledge:
                blocks.append(f"{code}: 常见 HTTP 状态码，请结合日志字段分析。")
                continue

            blocks.append(
                "\n".join(
                    [
                        f"{code} {knowledge['name']}",
                        f"解释：{knowledge['explanation']}",
                        f"常见原因：{'; '.join(knowledge['common_causes'])}",
                        f"排查建议：{'; '.join(knowledge['suggestions'])}",
                    ]
                )
            )

        return "\n\n".join(blocks)

    @staticmethod
    def _build_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "你是 CloudSupport AI 的 HTTP 日志分析专家。"
                        "请基于日志文本和状态码知识分析问题，不要编造日志中不存在的字段。"
                        "如果证据不足，请明确写入 missing_info。\n\n"
                        "必须只输出一个合法 JSON 对象，不要使用 Markdown 代码块，"
                        "不要在 JSON 前后添加解释性文本。\n\n"
                        "JSON schema：\n"
                        "{\n"
                        '  "problem_type": "问题类型，例如 upstream_error/gateway_timeout/client_abort/unknown",\n'
                        '  "status_code_explanation": "状态码解释",\n'
                        '  "problem_causes": ["问题原因"],\n'
                        '  "troubleshooting_suggestions": ["排查建议"],\n'
                        '  "detected_status_codes": [502],\n'
                        '  "evidence": ["从日志中提取的关键证据"],\n'
                        '  "missing_info": ["仍需补充的信息"],\n'
                        '  "confidence": 0.0\n'
                        "}"
                    ),
                ),
                (
                    "human",
                    (
                        "分析问题：{question}\n\n"
                        "识别到的状态码：{detected_status_codes}\n\n"
                        "状态码知识：\n{status_context}\n\n"
                        "日志文本：\n{log_text}\n\n"
                        "请输出结构化 JSON。"
                    ),
                ),
            ]
        )

    def _normalize_result(
        self,
        content: str,
        detected_status_codes: list[int],
    ) -> dict[str, Any]:
        """Parse and normalize the LLM JSON result."""
        try:
            result = json.loads(self._strip_code_fence(content))
        except json.JSONDecodeError:
            result = self._fallback_result(content, detected_status_codes)

        result.setdefault("problem_type", self._infer_problem_type(detected_status_codes))
        result.setdefault(
            "status_code_explanation",
            self._default_status_explanation(detected_status_codes),
        )
        result.setdefault("problem_causes", [])
        result.setdefault("troubleshooting_suggestions", [])
        result.setdefault("detected_status_codes", detected_status_codes)
        result.setdefault("evidence", [])
        result.setdefault("missing_info", [])
        result.setdefault("confidence", 0.5)

        return result

    @staticmethod
    def _strip_code_fence(content: str) -> str:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()

    def _fallback_result(
        self,
        raw_answer: str,
        detected_status_codes: list[int],
    ) -> dict[str, Any]:
        """Return valid JSON if the LLM responds with non-JSON text."""
        return {
            "problem_type": self._infer_problem_type(detected_status_codes),
            "status_code_explanation": self._default_status_explanation(
                detected_status_codes
            ),
            "problem_causes": [],
            "troubleshooting_suggestions": [],
            "detected_status_codes": detected_status_codes,
            "evidence": [raw_answer[:500]] if raw_answer else [],
            "missing_info": ["LLM 未返回合法 JSON，需要重新分析或检查 Prompt。"],
            "confidence": 0.3,
        }

    def _default_status_explanation(self, status_codes: list[int]) -> str:
        explanations = []
        for code in status_codes:
            knowledge = self.STATUS_CODE_KNOWLEDGE.get(code)
            if knowledge:
                explanations.append(f"{code}: {knowledge['explanation']}")
        return "；".join(explanations) if explanations else "未识别到明确状态码。"

    @staticmethod
    def _infer_problem_type(status_codes: list[int]) -> str:
        if 502 in status_codes:
            return "upstream_error"
        if 504 in status_codes:
            return "gateway_timeout"
        if 499 in status_codes:
            return "client_abort"
        return "unknown"

    @staticmethod
    def _build_llm() -> ChatOpenAI:
        provider = os.getenv("LLM_PROVIDER", "openai").lower()

        if provider == "qwen":
            return ChatOpenAI(
                model=os.getenv("QWEN_CHAT_MODEL", "qwen-plus"),
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url=os.getenv(
                    "QWEN_BASE_URL",
                    "https://dashscope.aliyuncs.com/compatible-mode/v1",
                ),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
            )

        return ChatOpenAI(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        )
