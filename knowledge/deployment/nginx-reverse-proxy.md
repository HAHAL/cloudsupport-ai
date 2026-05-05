# Nginx Reverse Proxy

## Scenario

适用于通过 Nginx 反向代理访问 FastAPI、SaaS 后端或 Web 控制台时出现 502、504、WebSocket / Streaming 中断或静态资源异常的场景。

## Symptoms

- Nginx 返回 502 或 504。
- upstream timed out 或 connection reset。
- 直接访问后端正常，通过代理失败。

## Possible Causes

- upstream 地址、端口或协议配置错误。
- proxy_read_timeout / proxy_connect_timeout 太短。
- 请求体大小限制不足。
- Header、Host、X-Forwarded-* 转发不完整。

## Troubleshooting Steps

1. 确认 Nginx upstream 指向正确容器或主机端口。
2. 查看 Nginx access log 和 error log。
3. 对比直接访问后端和通过代理访问结果。
4. 检查 timeout、body size 和 header 转发配置。
5. 重载 Nginx 配置并验证 `/health`。

## Required Information

- Nginx 配置片段
- access log / error log
- 后端服务地址和健康检查结果
- 失败请求 URL、状态码和 request_id

## Escalation Criteria

- 代理配置正确但上游服务仍异常。
- 后端服务在高并发或长请求下持续超时。
