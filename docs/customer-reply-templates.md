# 客户回复模板

本文档提供云产品和 LLM API 支持场景下的中英文客户回复模板。

## 1. API Key 鉴权失败

### 中文

您好，

感谢您的反馈。

根据目前提供的信息，请求返回鉴权失败，可能与 API Key、Authorization Header、签名参数或运行环境变量加载有关。为了继续排查，请您提供以下信息：

1. 脱敏后的请求 Header 和错误响应体
2. request ID 或 trace ID
3. 请求时间和时区
4. 使用的 Base URL、模型名称和 SDK 版本
5. API Key 是否在当前运行环境中正确加载

收到以上信息后，我们会继续协助确认鉴权链路。

技术支持团队

### English

Dear Customer,

Thank you for contacting us.

Based on the current information, the request appears to be failing at the authentication stage. This may be related to the API key, Authorization header, signature parameters, or runtime environment variable loading.

Could you please provide the following information:

1. Sanitized request headers and full error response body
2. Request ID or trace ID
3. Timestamp with timezone
4. Base URL, model name, and SDK version
5. Whether the API key is correctly loaded in the runtime environment

Once we receive the above information, we will continue the investigation.

Best regards,  
Technical Support Team

## 2. 429 限流

### 中文

您好，

当前错误显示请求可能触发了限流或配额限制。请您协助确认以下信息：

1. 请求时间范围
2. 峰值 QPS、RPM、TPM 和并发数
3. 使用的模型名称和工作空间
4. 是否启用了自动重试
5. 错误响应体和 request ID

临时建议降低并发、减少输入和输出 token，并为 429 增加指数退避重试。

技术支持团队

### English

Dear Customer,

The error indicates that the request may have hit a rate limit or quota limit.

Please provide:

1. Time range of the affected requests
2. Peak QPS, RPM, TPM, and concurrency
3. Model name and workspace
4. Whether automatic retry is enabled
5. Error response body and request ID

As a temporary mitigation, please reduce concurrency, reduce token usage, and add exponential backoff with jitter for 429 responses.

Best regards,  
Technical Support Team

## 3. Timeout 超时

### 中文

您好，

当前问题可能与请求体过大、模型推理耗时、网络链路或网关超时配置有关。请提供：

1. request ID
2. 请求时间和时区
3. 输入 token、输出 token、max_tokens 配置
4. 客户端和网关 timeout 配置
5. 是否使用流式输出

临时建议缩短上下文、减少输出长度，并适当增加客户端 timeout。

技术支持团队

### English

Dear Customer,

The timeout may be related to request size, model inference latency, network path, or gateway timeout settings.

Could you please provide:

1. Request ID
2. Timestamp with timezone
3. Input tokens, output tokens, and max_tokens configuration
4. Client and gateway timeout settings
5. Whether streaming output is enabled

As a temporary mitigation, please reduce context length, reduce output length, and increase client timeout where appropriate.

Best regards,  
Technical Support Team

## 4. RAG 问答不准确

### 中文

您好，

RAG 回答不准确通常需要同时检查检索结果和 Prompt。请提供：

1. 用户原始问题
2. 期望命中的知识库文档
3. 实际 Top-K 检索结果
4. chunk_size、chunk_overlap、Top-K 配置
5. 使用的 embedding 模型

我们会根据检索结果判断是召回问题、排序问题、知识库过期，还是 Prompt 约束不足。

技术支持团队

### English

Dear Customer,

RAG answer quality usually needs to be checked from both retrieval and prompting.

Please provide:

1. Original user question
2. Expected knowledge base document
3. Actual Top-K retrieved chunks
4. chunk_size, chunk_overlap, and Top-K settings
5. Embedding model name

We will check whether the issue is caused by recall, ranking, outdated knowledge, or insufficient prompt constraints.

Best regards,  
Technical Support Team

## 5. 模型返回内容不符合预期

### 中文

您好，

模型输出不符合预期可能与 Prompt、输出格式约束、temperature 或上下文质量有关。请提供完整 Prompt、输入样例、异常输出和模型参数。

建议先降低 temperature，明确输出 schema，并增加服务端 JSON 校验。

技术支持团队

### English

Dear Customer,

Unexpected model output may be related to the prompt, output format constraints, temperature, or context quality.

Please provide the full prompt, input example, unexpected output, and model parameters. We recommend lowering temperature, defining a clear output schema, and adding server-side JSON validation.

Best regards,  
Technical Support Team

## 6. 需要客户补充日志和请求参数

### 中文

您好，

为了进一步定位问题，请您补充以下信息：

1. 完整请求 URL、Method、Header 和 Body
2. 完整响应体
3. request ID 或 trace ID
4. 请求时间和时区
5. 客户端地域或源 IP
6. 复现步骤和影响范围

技术支持团队

### English

Dear Customer,

To continue the investigation, could you please provide:

1. Full request URL, method, headers, and body
2. Full response body
3. Request ID or trace ID
4. Timestamp with timezone
5. Client region or source IP
6. Reproduction steps and impact scope

Best regards,  
Technical Support Team

## 7. 需要升级研发排查

### 中文

您好，

根据目前信息，该问题可能需要进一步升级专项团队确认。升级前请补充 request ID、时间、区域、请求体、响应体和稳定复现步骤。

收到后，我们会整理问题摘要和证据，再继续推进后续排查。

技术支持团队

### English

Dear Customer,

Based on the current information, this issue may require further investigation by a specialized support or engineering team.

Before escalation, please provide the request ID, timestamp, region, request body, response body, and stable reproduction steps. Once we receive the information, we will prepare the issue summary and evidence for further investigation.

Best regards,  
Technical Support Team
