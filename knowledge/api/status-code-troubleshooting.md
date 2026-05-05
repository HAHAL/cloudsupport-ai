# API Status Code Troubleshooting

## Scenario

适用于企业 API 或 SaaS 后端接口返回 `400`、`401`、`403`、`404`、`408`、`429`、`500`、`502`、`503`、`504` 等状态码的通用排查。

## Symptoms

- 客户反馈接口调用失败。
- 网关、应用或客户端日志中出现 HTTP 状态码异常。
- 不同用户、区域或环境表现不一致。

## Possible Causes

- 请求参数或路径错误。
- 鉴权、权限或访问策略异常。
- 限流、配额或并发限制。
- 上游服务异常、依赖服务超时或网关配置不合理。

## Troubleshooting Steps

1. 明确状态码、接口路径、请求方法和错误响应。
2. 收集 request_id、时间点、请求参数和响应头。
3. 对比成功请求和失败请求。
4. 查看应用日志、网关日志和上游依赖状态。
5. 根据状态码类型进入专项排查。

## Required Information

- HTTP method、URL、status code
- request_id / trace_id
- 请求体、响应体、响应头
- 发生时间、影响范围和复现步骤

## Escalation Criteria

- 基础配置检查完成后仍无法定位。
- 多用户或关键业务路径持续受影响。
