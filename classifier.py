from enum import Enum


class QuestionCategory(str, Enum):
    """Supported technical support categories."""

    CDN = "CDN"
    DNS = "DNS"
    HTTPS = "HTTPS"
    VIDEO_PLAYBACK = "视频播放"
    KUBERNETES = "Kubernetes"
    OTHER = "其他"


class QuestionClassifier:
    """Simple keyword-based technical question classifier.

    The current implementation uses transparent rules. Later, classify() can
    be upgraded to call an AI model without changing API or service code.
    """

    KEYWORD_RULES: dict[QuestionCategory, set[str]] = {
        QuestionCategory.CDN: {
            "cdn",
            "cache",
            "缓存",
            "回源",
            "命中率",
            "刷新",
            "预热",
            "边缘节点",
            "加速域名",
            "源站",
        },
        QuestionCategory.DNS: {
            "dns",
            "解析",
            "域名解析",
            "cname",
            "a记录",
            "aaaa",
            "ns记录",
            "ttl",
            "dig",
            "nslookup",
        },
        QuestionCategory.HTTPS: {
            "https",
            "ssl",
            "tls",
            "证书",
            "握手",
            "加密",
            "过期",
            "公钥",
            "私钥",
            "cipher",
        },
        QuestionCategory.VIDEO_PLAYBACK: {
            "视频",
            "播放",
            "卡顿",
            "首帧",
            "黑屏",
            "花屏",
            "码率",
            "转码",
            "m3u8",
            "hls",
            "flv",
            "直播",
            "点播",
            "播放器",
        },
        QuestionCategory.KUBERNETES: {
            "kubernetes",
            "k8s",
            "pod",
            "deployment",
            "service",
            "ingress",
            "configmap",
            "secret",
            "namespace",
            "node",
            "kubectl",
            "容器",
            "集群",
        },
    }

    def classify(self, question: str) -> QuestionCategory:
        """Classify a user question into one technical category."""
        text = question.lower().strip()
        if not text:
            return QuestionCategory.OTHER

        scores = {
            category: self._score(text, keywords)
            for category, keywords in self.KEYWORD_RULES.items()
        }
        category, score = max(scores.items(), key=lambda item: item[1])

        if score <= 0:
            return QuestionCategory.OTHER
        return category

    @staticmethod
    def _score(text: str, keywords: set[str]) -> int:
        return sum(1 for keyword in keywords if keyword.lower() in text)

    def classify_with_ai(self, question: str) -> QuestionCategory:
        """Reserved extension point for future LLM-based classification."""
        return self.classify(question)
