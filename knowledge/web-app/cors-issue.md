# Web App CORS Issue

## Scenario

适用于浏览器访问 API 时出现跨域错误、预检请求失败、前端无法读取响应头或 Cookie 无法携带的场景。

## Symptoms

- 浏览器 Console 出现 CORS policy error。
- OPTIONS 预检请求失败。
- 后端接口直接 curl 正常，但浏览器请求失败。

## Possible Causes

- Access-Control-Allow-Origin 未配置或不匹配。
- Access-Control-Allow-Headers / Methods 缺失。
- Credential 模式下 Origin 或 Cookie 配置不正确。
- 反向代理未转发 OPTIONS 请求。

## Troubleshooting Steps

1. 检查浏览器 Console 和 Network 中的预检请求。
2. 确认 Origin、Method、Headers 和 Credential 配置。
3. 检查后端与反向代理的 CORS 响应头。
4. 使用 curl 模拟 OPTIONS 请求。
5. 对比测试环境和生产环境配置差异。

## Required Information

- 浏览器 Console 错误
- OPTIONS 请求和响应头
- 前端 Origin、API URL 和请求 Header
- 后端与代理配置片段

## Escalation Criteria

- 配置符合预期但浏览器仍稳定失败。
- 多环境出现不一致行为。
