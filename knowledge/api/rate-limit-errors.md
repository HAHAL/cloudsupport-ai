---
doc_id: api-rate-limit-errors
title: API 限流错误排查
version: v1.2.0
status: active
owner: support-team
effective_from: 2026-05-01
deprecated_at:
tags:
  - api
  - rate-limit
  - 429
---

# API Rate Limit Errors

## Scenario

适用于 API 返回 `429 Too Many Requests`、QPS / RPM / TPM / 并发限制、配额不足或重试风暴的场景。

## Symptoms

- API 返回 `429`。
- 高峰期或批处理任务中失败率上升。
- 重试后短时间恢复，但高并发下再次失败。

## Possible Causes

- 请求频率超过接口限制。
- 并发任务过多。
- Token 用量、请求量或账户配额不足。
- 客户端重试策略过于激进。

## Troubleshooting Steps

1. 统计失败时间段的请求量、并发数和错误比例。
2. 检查 API 响应头或控制台中的限流与配额信息。
3. 降低并发，增加指数退避和 jitter。
4. 拆分批处理任务，避免集中突发请求。
5. 如业务需要，申请更高配额或调整调用策略。

## Required Information

- 时间范围和时区
- request_id 样例
- QPS / RPM / TPM / 并发数
- 当前重试策略和业务影响

## Escalation Criteria

- 客户已按建议降频但仍持续触发限流。
- 控制台配额显示正常但 API 持续返回 429。
