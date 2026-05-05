# API Timeout Errors

## Scenario

适用于 API 请求返回 `408`、`504`、客户端超时、网关超时或上游响应过慢的场景。

## Symptoms

- API 返回 `504 Gateway Timeout`。
- 日志中出现 `request_time=60.001`、`upstream_response_time=60.000`。
- 客户端提示 read timeout、connection reset 或 upstream timed out。

## Possible Causes

- 上游服务处理耗时过长。
- 请求体过大或模型推理时间过长。
- 数据库、缓存或第三方依赖响应慢。
- 网关、代理或客户端 timeout 设置过短。

## Troubleshooting Steps

1. 对比 request_time 和 upstream_response_time。
2. 检查应用慢日志、数据库慢查询和依赖服务耗时。
3. 确认网关、反向代理和客户端 timeout 配置。
4. 使用最小请求复现，排除请求体过大或参数异常。
5. 收集 request_id、日志片段和监控截图。

## Required Information

- request_id / trace_id
- 完整日志和发生时间
- endpoint、请求参数和响应体
- 客户端 timeout 配置和业务影响

## Escalation Criteria

- 多个接口或多个用户持续超时。
- 上游服务、数据库或平台侧疑似异常。
