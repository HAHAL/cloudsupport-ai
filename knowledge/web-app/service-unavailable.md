# Web App Service Unavailable

## Scenario

适用于企业后台或 SaaS 应用返回 `500`、`502`、`503`、`504`、白屏或服务不可用的场景。

## Symptoms

- 页面提示 Service Unavailable。
- API 返回 5xx。
- 应用日志出现 exception、upstream error 或 timeout。

## Possible Causes

- 应用进程异常或实例不健康。
- 数据库、缓存、对象存储或第三方依赖不可用。
- 反向代理、负载均衡或网关配置异常。
- 发布变更导致运行时配置缺失。

## Troubleshooting Steps

1. 检查容器、进程和实例健康状态。
2. 查看应用错误日志和启动日志。
3. 检查数据库、缓存和外部依赖连通性。
4. 回看最近发布、配置变更和资源使用情况。
5. 收集 request_id、时间点和影响范围。

## Required Information

- 错误页面截图或 API 响应
- request_id、日志片段和时间范围
- 最近发布或配置变更记录
- 影响用户、租户和业务路径

## Escalation Criteria

- 多实例或多租户持续不可用。
- 平台依赖、数据库或运行环境疑似异常。
