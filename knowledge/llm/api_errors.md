# LLM API 401/429/5xx 排查

## 适用场景

适用于调用大模型 API 时出现 `401 Unauthorized`、`429 Too Many Requests`、`500/502/503/504` 等错误。

## 常见现象

- API 返回 401，提示 invalid api key、unauthorized、signature error。
- API 返回 429，提示 rate limit、quota exceeded、too many requests。
- API 返回 5xx，调用偶发失败或超时。
- 本地环境正常，服务器环境失败。
- 同一 Key 在不同项目或模型上表现不同。

## 可能原因

- API Key 配置错误、过期、被禁用或没有对应模型权限。
- 请求使用了错误的 Base URL、模型名或 API 版本。
- 账号余额不足、日额度耗尽或 QPS/TPM/RPM 达到上限。
- 并发过高且没有指数退避重试。
- 请求体过大、上下文过长或流式响应被代理中断。
- 服务商侧临时故障或区域网络异常。

## 排查步骤

1. 确认服务端环境变量中的 API Key 是否正确加载。
2. 检查 Base URL、模型名称、API 版本和 SDK 版本。
3. 对 401，使用最小请求验证 Key 是否有效，确认账号和模型权限。
4. 对 429，查看 QPS、RPM、TPM、并发数和账号额度。
5. 对 5xx，记录 request_id、时间点、模型名和请求参数，增加重试和熔断。
6. 检查代理、网关、Nginx 超时设置是否中断流式响应。
7. 对超长 Prompt，统计 token 数并减少无关上下文。

## 客户需要提供的信息

- 错误状态码、响应体和 request_id。
- 模型名称、Base URL、SDK 版本。
- 请求时间、并发量、QPS/RPM/TPM。
- 请求体大小、Prompt token、输出 token。
- 是否使用代理、网关、私有网络或企业防火墙。
- 账号额度、余额和模型权限截图。

## 升级专家/研发的条件

- 账号权限和额度正常但持续 401/429。
- 同一请求在服务商控制台可成功，本地或服务器失败。
- 大面积 5xx 且重试后仍失败。
- 服务商返回 request_id，需要平台侧查询调用链路。
