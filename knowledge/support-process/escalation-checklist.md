---
doc_id: escalation-checklist
title: 升级信息收集清单
version: v1.0.0
status: active
owner: support-operations
effective_from: 2026-05-01
deprecated_at:
tags:
  - support-process
  - escalation
  - required-information
---

# Escalation Checklist

## Scenario

适用于问题需要升级研发、运维、平台或专项支持团队前的信息收集。

## Required Information

- 问题摘要和影响范围
- 发生时间、时区和持续时长
- request_id / trace_id
- 受影响账号、租户、环境或 workspace
- 错误码、响应体、日志片段和截图
- 复现步骤、成功/失败对比
- 已完成的排查动作
- 临时处理方案和客户期望

## Suggested Summary

请用以下结构整理升级摘要：

1. 问题现象
2. 影响范围
3. 关键证据
4. 已排除项
5. 需要协助确认的问题
6. 建议负责人

## Escalation Criteria

- 多用户、多租户或关键业务流程受影响。
- 一线支持无法通过配置、日志和文档确认根因。
- 需要服务端 trace、平台日志或产品工程判断。
