# LLM API Errors

## Scenario

适用于 AI 应用调用 LLM API 时出现鉴权失败、权限不足、限流、上下文超长、流式输出中断或服务端错误的场景。

## Symptoms

- `401`、`403`、`429`、`5xx` 或 timeout。
- stream interrupted。
- context_length_exceeded。

## Possible Causes

- API Key、模型权限或 workspace 配置错误。
- RPM、TPM、QPS 或并发超限。
- Prompt、历史消息或 RAG 上下文过长。
- 客户端、代理或网关 timeout 设置不合理。

## Troubleshooting Steps

1. 收集 request_id、模型名称、endpoint 和 SDK 版本。
2. 检查错误码、响应体和响应头。
3. 确认 Key、权限、配额、账单和限流信息。
4. 对比流式和非流式调用。
5. 缩短上下文或降低并发进行验证。

## Required Information

- request_id / trace_id
- 模型名称、endpoint、workspace
- 请求体脱敏样例和错误响应
- 请求量、并发、token 使用量和重试策略

## Escalation Criteria

- 权限、配额和请求格式均确认正常，但错误持续复现。
- 多个客户或关键业务流程受影响。
