---
doc_id: api-rate-limit-errors
title: API 限流错误排查旧版
version: v1.0.0
status: deprecated
owner: support-team
effective_from: 2026-03-01
deprecated_at: 2026-05-01
tags:
  - api
  - rate-limit
  - 429
---

# API 限流错误排查旧版

## Scenario

适用于 API 返回 `429 Too Many Requests` 的历史排查流程。该版本保留用于对比旧知识，不参与默认检索。

## Symptoms

- API 调用返回 `429`。
- 批量任务或高峰时段失败率上升。

## Possible Causes

- 请求频率超过接口限制。
- 账户配额不足。
- 客户端短时间内重复重试。

## Troubleshooting Steps

1. 降低请求频率并观察错误是否缓解。
2. 检查控制台中的调用量和配额信息。
3. 补充 request_id、时间范围和调用量数据。

## Required Information

- 时间范围和时区
- request_id
- 当前 QPS、并发数和重试策略

## Escalation Criteria

- 降频后仍持续返回 429。
- 配额显示正常但接口仍异常限流。
