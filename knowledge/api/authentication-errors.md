# API Authentication Errors

## Scenario

适用于企业 API、AI API 或 SaaS OpenAPI 调用返回 `401 Unauthorized`、Token 失效、签名失败或鉴权 Header 缺失的场景。

## Symptoms

- API 返回 `401 Unauthorized`。
- 错误信息提示 API Key、Token、Signature 或 Authorization Header 无效。
- 本地环境可以调用，服务器环境调用失败。

## Possible Causes

- API Key、Token 或 AccessKey 已过期、填错或未加载到运行环境。
- Authorization Header 格式错误。
- 请求时间戳、签名算法或签名字符串不一致。
- 使用了错误的环境、项目、租户或模型服务 Endpoint。

## Troubleshooting Steps

1. 使用最小请求验证 API Key 或 Token 是否有效。
2. 检查运行时环境变量是否正确加载。
3. 确认 Authorization Header 格式和签名算法。
4. 对比成功请求和失败请求的 endpoint、headers、timestamp 和 request body。
5. 收集 request_id、时间点和完整错误响应。

## Required Information

- request_id / trace_id
- 请求时间和时区
- endpoint、method、headers 和错误响应
- 使用的环境、项目、租户或 workspace

## Escalation Criteria

- 确认凭证、签名和权限均正确，但请求仍稳定失败。
- 多个客户或多个环境同时出现鉴权异常。
