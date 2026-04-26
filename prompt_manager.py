from langchain_core.prompts import ChatPromptTemplate

from classifier import QuestionCategory


class PromptManager:
    """Centralized prompt templates for CloudSupport AI.

    All prompts return JSON-compatible structured output. The templates keep
    dynamic variables such as context/question/log_text/ticket_text explicit so
    service code can pass runtime values through LangChain.
    """

    @staticmethod
    def main_qa_prompt() -> ChatPromptTemplate:
        """General technical support QA prompt with structured output."""
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "你是 CloudSupport AI，一名资深云产品技术支持专家。"
                        "请用准确、可执行的方式回答技术支持问题。\n\n"
                        f"{PromptManager._json_output_rule()}\n"
                        "JSON 字段说明：\n"
                        "- answer: 直接回答用户问题。\n"
                        "- category: 问题类别，例如 cdn/dns/video/general。\n"
                        "- possible_causes: 可能原因数组。\n"
                        "- troubleshooting_steps: 排查步骤数组。\n"
                        "- recommended_actions: 建议动作数组。\n"
                        "- confidence: 0 到 1 的置信度。\n"
                        "- missing_info: 仍需用户补充的信息数组。"
                    ),
                ),
                (
                    "human",
                    (
                        "问题分类：{category}\n\n"
                        "用户问题：{question}\n\n"
                        "请按统一 JSON 格式输出。"
                    ),
                ),
            ]
        )

    @staticmethod
    def rag_enhanced_prompt() -> ChatPromptTemplate:
        """RAG prompt that grounds the answer in retrieved context."""
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "你是 CloudSupport AI，一名严格基于知识库回答的技术支持专家。"
                        "你必须优先依据给定 context 作答，不能编造上下文不存在的产品能力、配置项、"
                        "错误码含义或承诺。\n\n"
                        "防幻觉规则：\n"
                        "1. 如果 context 足够，基于 context 给出答案和排查步骤。\n"
                        "2. 如果 context 不足，明确说明“不足以确认”，并列出需要补充的信息。\n"
                        "3. 不要输出无法从 context 或常规技术排查逻辑支持的结论。\n"
                        "4. 引用依据时使用 context 中的 source 标识。\n\n"
                        f"{PromptManager._json_output_rule()}\n"
                        "JSON 字段说明：\n"
                        "- answer: 基于 context 的回答。\n"
                        "- category: 问题类别。\n"
                        "- evidence: 使用到的依据数组，每项包含 source 和 summary。\n"
                        "- possible_causes: 可能原因数组。\n"
                        "- troubleshooting_steps: 排查步骤数组。\n"
                        "- recommended_actions: 建议动作数组。\n"
                        "- missing_info: 仍需补充的信息数组。\n"
                        "- confidence: 0 到 1 的置信度。"
                    ),
                ),
                (
                    "human",
                    (
                        "问题分类：{category}\n\n"
                        "context：\n{context}\n\n"
                        "question：{question}\n\n"
                        "请按统一 JSON 格式输出。"
                    ),
                ),
            ]
        )

    @staticmethod
    def log_analysis_prompt() -> ChatPromptTemplate:
        """Prompt for technical log analysis."""
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "你是 CloudSupport AI 的日志分析专家。请分析日志中的异常、错误模式、"
                        "可能根因和下一步排查建议。不要臆造日志中不存在的字段或错误。\n\n"
                        f"{PromptManager._json_output_rule()}\n"
                        "JSON 字段说明：\n"
                        "- summary: 日志整体摘要。\n"
                        "- severity: low/medium/high/critical。\n"
                        "- detected_errors: 检测到的错误数组。\n"
                        "- root_causes: 可能根因数组。\n"
                        "- timeline: 关键时间线数组。\n"
                        "- recommended_actions: 建议动作数组。\n"
                        "- missing_info: 仍需补充的信息数组。\n"
                        "- confidence: 0 到 1 的置信度。"
                    ),
                ),
                (
                    "human",
                    (
                        "日志上下文：\n{context}\n\n"
                        "日志内容：\n{log_text}\n\n"
                        "分析问题：{question}\n\n"
                        "请按统一 JSON 格式输出。"
                    ),
                ),
            ]
        )

    @staticmethod
    def ticket_classification_prompt() -> ChatPromptTemplate:
        """Prompt for support ticket classification and routing."""
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "你是 CloudSupport AI 的工单分诊专家。请根据工单内容判断产品类别、"
                        "问题类型、优先级和应分派团队。\n\n"
                        "分类范围：\n"
                        "- category: cdn/dns/video/general。\n"
                        "- priority: p0/p1/p2/p3。\n"
                        "- intent: troubleshooting/configuration/billing/consulting/bug/other。\n\n"
                        f"{PromptManager._json_output_rule()}\n"
                        "JSON 字段说明：\n"
                        "- category: 工单产品类别。\n"
                        "- intent: 工单意图。\n"
                        "- priority: 优先级。\n"
                        "- assigned_team: 建议分派团队。\n"
                        "- reason: 分类理由。\n"
                        "- keywords: 命中的关键词数组。\n"
                        "- missing_info: 仍需补充的信息数组。\n"
                        "- confidence: 0 到 1 的置信度。"
                    ),
                ),
                (
                    "human",
                    (
                        "工单上下文：\n{context}\n\n"
                        "工单内容：\n{ticket_text}\n\n"
                        "用户问题：{question}\n\n"
                        "请按统一 JSON 格式输出。"
                    ),
                ),
            ]
        )

    @staticmethod
    def support_qa_prompt() -> ChatPromptTemplate:
        """Backward-compatible RAG QA prompt used by RAGService."""
        return PromptManager.rag_enhanced_prompt()

    @staticmethod
    def format_prompt(
        prompt: ChatPromptTemplate,
        *,
        question: str = "",
        context: str = "",
        category: str = QuestionCategory.OTHER.value,
        log_text: str = "",
        ticket_text: str = "",
    ):
        """Format any managed prompt with a consistent set of variables."""
        return prompt.format_messages(
            question=question,
            context=context,
            category=category,
            log_text=log_text,
            ticket_text=ticket_text,
        )

    @staticmethod
    def empty_context_answer(category: QuestionCategory) -> str:
        return (
            f"当前问题已识别为 {category.value} 类问题，但知识库中没有检索到足够相关的资料。"
            "建议补充错误码、请求 URL、域名、时间范围、日志片段、用户地域和复现步骤后再分析。"
        )

    @staticmethod
    def _json_output_rule() -> str:
        return (
            "输出要求：只输出一个合法 JSON 对象，不要使用 Markdown 代码块，"
            "不要在 JSON 前后添加解释性文本。所有数组字段即使为空也必须返回 []。"
        )
