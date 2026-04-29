# RAG 工作流与检索质量排查

本文档说明 CloudSupport AI 中 RAG 风格知识库问答的处理流程，以及常见检索质量问题的排查方法。

## 1. 文档上传

知识库文档放在 `knowledge/` 目录下，按产品或场景分类，例如：

```text
knowledge/cdn/
knowledge/dns/
knowledge/https/
knowledge/video/
knowledge/kubernetes/
knowledge/llm/
```

支持 Markdown、TXT 和 PDF 等本地文档格式。

## 2. 文档解析

文档加载模块读取本地文件，并保留来源路径、分类等 metadata。metadata 用于后续过滤、引用来源展示和问题定位。

## 3. 文本切分 chunk

长文档会被切分为 chunk。常见参数包括：

- `chunk_size`: 单个片段长度。
- `chunk_overlap`: 相邻片段重叠长度。

过大的 chunk 会引入噪声，过小的 chunk 可能丢失上下文。

## 4. Embedding / 关键词索引

每个 chunk 会被转换为向量并写入 Chroma。对于技术支持系统，也可以补充关键词索引，用于错误码、产品名、request ID 等精确匹配场景。

## 5. Top-K 检索

用户问题进入检索流程后，系统会基于相似度返回 Top-K 相关片段。Top-K 过小可能召回不足，Top-K 过大可能导致 Prompt 过长。

## 6. Prompt 拼接

Prompt 通常包含：

- 用户问题
- 检索到的上下文
- 输出格式要求
- 防幻觉约束
- 缺失信息处理规则

## 7. 调用大模型

LLM 根据问题和上下文生成答案。对于技术支持场景，Prompt 应要求模型基于上下文回答，不要编造产品能力、配置项或错误码含义。

## 8. 返回答案与引用来源

响应中应包含：

- answer
- retrieved contents
- references
- metadata

引用来源可以帮助支持工程师快速验证答案依据。

## 常见问题

### 检索不到

可能原因：

- 文档未成功入库。
- metadata filter 过滤条件错误。
- 用户问题与知识库术语差异较大。
- embedding 模型不适合当前语言或领域。

优化建议：

- 检查入库日志和 Chroma collection。
- 增加 query rewrite。
- 补充同义词、错误码和产品别名。

### 检索错

可能原因：

- chunk 包含多个主题。
- 文档标题缺失。
- Top-K 太大，引入弱相关内容。

优化建议：

- 调整 chunk_size。
- 在 chunk metadata 中保留标题和产品分类。
- 增加 reranking。

### chunk 太大或太小

chunk 太大：

- 检索结果噪声多。
- Prompt 变长。
- 模型更容易忽略关键句。

chunk 太小：

- 上下文不完整。
- 排查步骤被切断。
- 答案缺少必要背景。

优化建议：

- 技术支持文档可从 `500-1000` 字符开始调参。
- 保留适度 overlap。
- 用真实问题做评测。

### 召回内容不相关

排查方法：

1. 打印 query、Top-K chunk、score 和 metadata。
2. 检查是否误用了分类过滤。
3. 检查 embedding 模型是否支持当前语言。
4. 对问题做标准化改写。

### Prompt 太长

优化建议：

- 降低 Top-K。
- 对长 chunk 做摘要。
- 移除重复上下文。
- 限制历史对话长度。

### 模型幻觉

优化建议：

- Prompt 中明确“只能基于 context 回答”。
- 要求证据不足时输出 `missing_info`。
- 返回 references 给支持工程师核验。
- 对高风险建议增加人工确认。

### 知识库过期

排查方法：

- 检查文档更新时间。
- 检查索引是否重建。
- 对比知识库内容与产品最新文档。

优化建议：

- 建立文档版本字段。
- 对过期文档增加归档策略。
- 增加定期 RAG 评测。
