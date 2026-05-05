---
doc_id: rag-retrieval-quality
title: RAG 检索质量排查
version: v1.0.0
status: active
owner: ai-support-team
effective_from: 2026-05-01
deprecated_at:
tags:
  - ai-support
  - rag
  - retrieval
  - knowledge-base
---

# RAG Retrieval Quality

## Scenario

适用于企业知识库问答召回不准、回答缺少依据、相关文档未命中或模型回答偏离知识库的场景。

## Symptoms

- 用户问题有对应文档，但检索不到。
- 检索结果相关性低。
- 回答引用了不相关内容。

## Possible Causes

- chunk size 或 overlap 不合理。
- 文档标题、关键词和 metadata 缺失。
- Embedding 模型与语言或业务术语不匹配。
- Top-K、过滤条件或重排序策略不合适。

## Troubleshooting Steps

1. 确认知识库中是否存在正确答案。
2. 查看命中文档、分数和 chunk 内容。
3. 调整 chunk size、overlap 和 Top-K。
4. 补充标题、关键词、同义词和 metadata。
5. 建立评测问题集，持续跟踪召回质量。

## Required Information

- 用户问题
- 期望命中的文档
- 实际命中文档和分数
- chunk 配置、Embedding 模型和 Top-K 设置

## Escalation Criteria

- 多类问题系统性召回不准。
- 检索正确但生成答案仍偏离上下文。
