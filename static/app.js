const workflows = {
  chat: {
    label: "知识库问答",
    endpoint: "/chat",
    fields: [
      {
        name: "question",
        label: "技术支持问题",
        type: "textarea",
        value: "LLM API 返回 429 Too Many Requests，应该如何排查？",
      },
    ],
  },
  triage: {
    label: "工单分诊",
    endpoint: "/ticket-triage",
    fields: [
      { name: "title", label: "工单标题", value: "Enterprise customer LLM API returns 403" },
      {
        name: "description",
        label: "工单描述",
        type: "textarea",
        value:
          "The customer reports 403 Forbidden when calling chat/completions from production. The issue affects enterprise users in Singapore region. Need first response and routing advice.",
      },
      { name: "customer_level", label: "客户等级", value: "enterprise" },
      { name: "affected_product", label: "受影响产品", value: "LLM API" },
    ],
  },
  apiDebug: {
    label: "API 报错分析",
    endpoint: "/api-debug",
    fields: [
      { name: "method", label: "HTTP 方法", value: "POST" },
      { name: "url", label: "请求 URL", value: "https://api.example.com/v1/chat/completions" },
      { name: "status_code", label: "状态码", value: "429", number: true },
      { name: "request_id", label: "请求 ID", value: "req_sample_20260505_001" },
      {
        name: "error_message",
        label: "错误信息",
        type: "textarea",
        value: "Too Many Requests: rate limit exceeded for current workspace.",
      },
    ],
  },
  logAnalyze: {
    label: "日志分析",
    endpoint: "/log-analyze",
    fields: [
      {
        name: "log_text",
        label: "日志内容",
        type: "textarea",
        value:
          '2026-05-05T10:15:20+08:00 status=504 request_time=60.001 upstream_response_time=60.000 request_id=req_sample_001 error="upstream timed out"',
      },
      { name: "question", label: "分析重点", value: "Why did this API request return 504?" },
    ],
  },
  reply: {
    label: "客户回复生成",
    endpoint: "/ticket-reply",
    fields: [
      { name: "ticket_title", label: "工单标题", value: "LLM API timeout during peak traffic" },
      {
        name: "ticket_description",
        label: "工单描述",
        type: "textarea",
        value:
          "Customer reports timeout when calling the model endpoint. Current evidence shows long request duration but no complete request body yet.",
      },
      {
        name: "analysis_context",
        label: "分析上下文",
        value:
          "Possible timeout or request-size issue. Need request ID, timestamp, model name, and retry behavior.",
      },
      { name: "customer_name", label: "客户称呼", value: "Customer" },
    ],
  },
  escalation: {
    label: "升级信息收集",
    endpoint: "/escalation-info",
    fields: [
      { name: "issue_summary", label: "问题摘要", value: "LLM API returns persistent 504 for production requests" },
      { name: "product_area", label: "产品区域", value: "LLM" },
      { name: "observed_error", label: "观察到的错误", value: "504 Gateway Timeout, request_id=req_sample_002" },
      { name: "business_impact", label: "业务影响", value: "Production workflow is delayed for multiple enterprise users." },
    ],
  },
  knowledgeStatus: {
    label: "知识库状态",
    endpoint: "/knowledge/status",
    method: "GET",
    fields: [],
  },
  knowledgeVersions: {
    label: "文档版本列表",
    endpoint: "/knowledge/versions",
    method: "GET",
    fields: [],
  },
  knowledgeReindex: {
    label: "重建知识库索引",
    endpoint: "/knowledge/reindex",
    fields: [{ name: "force", label: "强制重建", type: "checkbox", value: true }],
  },
  previewChunks: {
    label: "文档切分预览",
    endpoint: "/knowledge/preview-chunks",
    fields: [
      {
        name: "text",
        label: "预览文本",
        type: "textarea",
        value: "这里是一段用于测试文档切分的企业技术支持知识内容。它包含 API 报错、权限异常、日志分析和升级信息收集等场景。",
      },
      { name: "file_path", label: "知识库文件路径", value: "knowledge/ai-support/rag-retrieval-quality.md" },
      { name: "chunk_size", label: "chunk_size", value: "800", number: true },
      { name: "chunk_overlap", label: "chunk_overlap", value: "120", number: true },
    ],
  },
  knowledgeSearch: {
    label: "知识库检索测试",
    endpoint: "/knowledge/search",
    fields: [
      { name: "query", label: "检索问题", value: "企业知识库问答结果不准确，应该如何排查？" },
      { name: "top_k", label: "top_k", value: "4", number: true },
      { name: "include_deprecated", label: "包含 deprecated 历史知识", type: "checkbox", value: false },
    ],
  },
  knowledgeDeprecate: {
    label: "标记知识废弃",
    endpoint: "/knowledge/deprecate",
    fields: [
      { name: "doc_id", label: "doc_id", value: "api-rate-limit-errors" },
      { name: "version", label: "version", value: "v1.0.0" },
      { name: "deprecated_at", label: "deprecated_at", value: "2026-05-01" },
      { name: "reason", label: "reason", value: "Replaced by v1.2.0" },
    ],
  },
};

const fieldLabels = {
  category: "问题分类",
  ticket_type: "工单类型",
  problem_type: "问题类型",
  severity: "严重级别",
  priority: "优先级",
  confidence: "置信度",
  summary: "问题摘要",
  issue_summary: "问题摘要",
  suggested_summary: "建议摘要",
  possible_causes: "可能原因",
  likely_causes: "可能原因",
  problem_causes: "可能原因",
  troubleshooting_steps: "排查步骤",
  troubleshooting_suggestions: "排查步骤",
  next_steps: "下一步动作",
  next_actions: "下一步动作",
  action_items: "处理动作",
  need_more_info: "需要补充的信息",
  required_information: "需要补充的信息",
  required_info: "需要补充的信息",
  required_customer_info: "需要客户补充的信息",
  first_response_actions: "首轮处理动作",
  customer_reply_suggestion: "客户回复建议",
  reply: "客户回复草稿",
  customer_reply: "客户回复草稿",
  references: "参考来源",
  retrieved_contents: "检索内容",
  escalation_team: "建议升级团队",
  assigned_team: "建议处理团队",
  suggested_owner: "建议负责人",
  recommended_owner: "建议负责人",
  escalation_criteria: "升级条件",
  escalation_summary: "升级摘要",
  missing_information: "缺失信息",
  missing_info: "缺失信息",
  temporary_workaround: "临时处理建议",
  risk_level: "风险等级",
  extracted_signals: "关键日志信号",
  request_id: "请求 ID",
  status_code: "状态码",
  detected_status_codes: "状态码",
  request_time: "请求耗时",
  upstream_response_time: "上游响应耗时",
  error: "错误信息",
  answer: "知识库回答",
  diagnosis: "诊断信息",
  intent: "工单意图",
  reason: "判断依据",
  impact_scope: "影响范围",
  status_code_explanation: "状态码解释",
  knowledge_dir: "知识库目录",
  vector_store: "向量库",
  chroma_dir: "Chroma 目录",
  collection: "Collection",
  chunk_size: "chunk_size",
  chunk_overlap: "chunk_overlap",
  top_k: "top_k",
  provider_ready: "provider_ready",
  mode: "当前模式",
  document_count: "文档总数",
  active_count: "active 数量",
  deprecated_count: "deprecated 数量",
  draft_count: "draft 数量",
  supported_file_types: "支持文件类型",
  indexed_status: "索引状态",
  message: "说明",
  documents: "文档列表",
  owner: "维护团队",
  effective_from: "生效日期",
  deprecated_at: "废弃日期",
  document_hash: "文档 Hash",
  content_hash: "内容 Hash",
  chunk_count: "chunk 数量",
  chunks: "切分结果",
  chunk_id: "chunk ID",
  length: "长度",
  content_preview: "内容预览",
  include_deprecated: "包含历史知识",
  results: "检索结果",
  new_status: "新状态",
};

let currentWorkflow = "chat";
let lastResult = null;
let lastReportText = "";
let rawJsonOpen = false;

const nav = document.getElementById("nav");
const title = document.getElementById("workflowTitle");
const fields = document.getElementById("fields");
const form = document.getElementById("workflowForm");
const result = document.getElementById("result");
const submitButton = document.getElementById("submitButton");

function renderNav() {
  nav.innerHTML = "";
  for (const [key, workflow] of Object.entries(workflows)) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = workflow.label;
    button.className = key === currentWorkflow ? "active" : "";
    button.addEventListener("click", () => {
      currentWorkflow = key;
      lastResult = null;
      lastReportText = "";
      rawJsonOpen = false;
      renderNav();
      renderFields();
      renderEmptyState();
    });
    nav.appendChild(button);
  }
}

function renderFields() {
  const workflow = workflows[currentWorkflow];
  title.textContent = workflow.label;
  fields.innerHTML = "";
  workflow.fields.forEach((field) => {
    const label = document.createElement("label");
    label.textContent = field.label;
    label.htmlFor = field.name;
    fields.appendChild(label);

          const input = document.createElement(field.type === "textarea" ? "textarea" : "input");
          input.id = field.name;
          input.name = field.name;
          if (field.type === "checkbox") {
            input.type = "checkbox";
            input.checked = Boolean(field.value);
          } else {
            input.value = field.value || "";
          }
          if (field.number) input.type = "number";
          fields.appendChild(input);
        });
}

function renderEmptyState() {
  result.innerHTML = "";
  result.appendChild(
    node("div", "empty-state", "请在左侧输入问题或日志内容，然后点击执行分析。"),
  );
}

function collectPayload() {
  const payload = {};
  workflows[currentWorkflow].fields.forEach((field) => {
    const element = document.getElementById(field.name);
    if (field.type === "checkbox") {
      payload[field.name] = element.checked;
      return;
    }
    const value = element.value.trim();
    if (!value) return;
    payload[field.name] = field.number ? Number(value) : value;
  });
  return payload;
}

async function postJson(endpoint, payload) {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorText = await response.text();
    const error = new Error(errorText || "请求失败");
    error.status = response.status;
    throw error;
  }
  return response.json();
}

async function requestWorkflow(workflow, payload) {
  if (workflow.method === "GET") {
    const response = await fetch(workflow.endpoint);
    if (!response.ok) {
      const errorText = await response.text();
      const error = new Error(errorText || "请求失败");
      error.status = response.status;
      throw error;
    }
    return response.json();
  }
  return postJson(workflow.endpoint, payload);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  submitButton.disabled = true;
  submitButton.textContent = "处理中";
  result.innerHTML = "";
  result.appendChild(node("div", "empty-state", "正在分析，请稍候..."));

  try {
    const workflow = workflows[currentWorkflow];
    const payload = collectPayload();
    lastResult = await requestWorkflow(workflow, payload);
    rawJsonOpen = false;
    renderReport(currentWorkflow, lastResult);
  } catch (error) {
    lastResult = null;
    lastReportText = "";
    renderError(error);
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "执行分析";
  }
});

function renderReport(workflowKey, data) {
  result.innerHTML = "";
  const model = normalizeResult(workflowKey, data);
  lastReportText = buildReportText(model);

  result.appendChild(renderSummaryCard(model));
  model.sections.forEach((section) => {
    if (hasContent(section.content)) {
      result.appendChild(renderSection(section));
    }
  });
  result.appendChild(renderActionCard(data));
}

function normalizeResult(workflowKey, data) {
  if (data === null || data === undefined) {
    return genericModel(workflowKey, "无返回内容", data);
  }
  if (typeof data !== "object" || Array.isArray(data)) {
    return genericModel(workflowKey, "返回结果", data);
  }

  const builders = {
    chat: normalizeChat,
    triage: normalizeTriage,
    apiDebug: normalizeApiDebug,
    logAnalyze: normalizeLogAnalyze,
    reply: normalizeReply,
    escalation: normalizeEscalation,
    knowledgeStatus: normalizeKnowledgeStatus,
    knowledgeVersions: normalizeKnowledgeVersions,
    knowledgeReindex: normalizeKnowledgeReindex,
    previewChunks: normalizePreviewChunks,
    knowledgeSearch: normalizeKnowledgeSearch,
    knowledgeDeprecate: normalizeKnowledgeDeprecate,
  };
  return (builders[workflowKey] || genericModel)(workflowKey, data);
}

function normalizeChat(_, data) {
  const summary = data.suggested_summary || data.answer || data.question || "知识库问答结果";
  return {
    title: "CloudSupport AI 诊断报告",
    summaryItems: [
      ["问题分类", data.category],
      ["置信度", formatConfidence(data.confidence || data.metadata?.confidence)],
      ["建议处理团队", data.escalation_team || data.assigned_team],
      ["简短摘要", shortText(summary)],
    ],
    sections: [
      { title: "知识库回答", content: data.answer, type: "text" },
      {
        title: "诊断信息",
        content: compactObject({
          问题分类: data.category,
          置信度: formatConfidence(data.confidence || data.metadata?.confidence),
          可能原因: data.diagnosis?.possible_causes || data.possible_causes,
          下一步动作: data.diagnosis?.next_actions || data.next_actions,
        }),
        type: "kv",
      },
      { title: "建议摘要", content: data.suggested_summary, type: "text" },
      { title: "需要补充的信息", content: firstArray(data.need_more_info, data.required_information, data.required_info, data.missing_info), type: "list" },
      { title: "升级条件", content: data.escalation_criteria, type: "list" },
      { title: "参考来源", content: firstArray(data.references, data.retrieved_contents), type: "references" },
    ],
  };
}

function normalizeTriage(_, data) {
  return {
    title: "工单分诊报告",
    summaryItems: [
      ["问题分类", data.category],
      ["优先级", data.priority],
      ["建议处理团队", data.suggested_owner || data.assigned_team],
      ["置信度", formatConfidence(data.confidence)],
    ],
    sections: [
      {
        title: "工单分诊结果",
        content: compactObject({
          工单类型: data.intent,
          优先级: data.priority,
          问题摘要: data.reason,
          建议负责人: data.suggested_owner || data.assigned_team,
          "SLA 建议": slaFromPriority(data.priority),
          影响范围: data.impact_scope,
        }),
        type: "kv",
      },
      { title: "首轮处理动作", content: firstArray(data.first_response_actions, data.next_actions, data.action_items), type: "list" },
      { title: "需要补充的信息", content: firstArray(data.need_more_info, data.required_info, data.missing_info), type: "list" },
    ],
  };
}

function normalizeApiDebug(_, data) {
  return {
    title: "API 报错分析报告",
    summaryItems: [
      ["问题分类", data.problem_type || data.category],
      ["严重级别", data.severity],
      ["置信度", formatConfidence(data.confidence)],
      ["简短摘要", data.issue_summary],
    ],
    sections: [
      {
        title: "API 报错分析",
        content: compactObject({
          问题分类: data.problem_type,
          严重级别: data.severity,
          问题摘要: data.issue_summary,
          状态码解释: data.status_code_explanation,
        }),
        type: "kv",
      },
      { title: "可能原因", content: firstArray(data.possible_causes, data.likely_causes), type: "list" },
      { title: "排查步骤", content: data.troubleshooting_steps, type: "list" },
      { title: "需要客户补充的信息", content: firstArray(data.need_more_info, data.required_customer_info, data.required_info), type: "list" },
      { title: "临时处理建议", content: data.temporary_workaround, type: "list" },
      { title: "客户回复建议", content: buildApiCustomerSuggestion(data), type: "text" },
    ],
  };
}

function normalizeLogAnalyze(_, data) {
  const signals = extractLogSignals(collectPayload().log_text || "");
  return {
    title: "日志分析报告",
    summaryItems: [
      ["问题分类", data.problem_type],
      ["状态码", firstArray(data.detected_status_codes)?.join(", ")],
      ["置信度", formatConfidence(data.confidence)],
      ["简短摘要", data.status_code_explanation],
    ],
    sections: [
      {
        title: "日志分析结果",
        content: compactObject({
          问题摘要: data.status_code_explanation,
          状态码: firstArray(data.detected_status_codes)?.join(", "),
          请求耗时: signals.request_time,
          上游响应耗时: signals.upstream_response_time,
          "请求 ID": signals.request_id,
          错误信息: signals.error,
        }),
        type: "kv",
      },
      { title: "可能原因", content: firstArray(data.possible_causes, data.problem_causes), type: "list" },
      { title: "排查步骤", content: firstArray(data.troubleshooting_steps, data.troubleshooting_suggestions), type: "list" },
      { title: "需要补充的信息", content: firstArray(data.need_more_info, data.missing_info), type: "list" },
      { title: "参考依据", content: data.evidence, type: "list" },
    ],
  };
}

function normalizeReply(_, data) {
  const reply = data.reply || data.customer_reply;
  return {
    title: "客户回复生成报告",
    summaryItems: [
      ["客户回复类型", "技术支持回复草稿"],
      ["语气", data.tone],
      ["置信度", formatConfidence(data.confidence)],
      ["简短摘要", data.subject],
    ],
    sections: [
      { title: "客户回复草稿", content: reply, type: "text" },
      { title: "下一步动作", content: firstArray(data.next_actions, data.action_items), type: "list" },
      { title: "需要客户确认的信息", content: data.need_customer_confirm, type: "list" },
      { title: "内部备注", content: data.internal_notes, type: "list" },
      { title: "升级条件", content: data.escalation_condition, type: "list" },
    ],
  };
}

function normalizeEscalation(_, data) {
  return {
    title: "升级信息收集报告",
    summaryItems: [
      ["问题分类", data.category],
      ["建议负责人", data.recommended_owner || data.escalation_team],
      ["风险等级", riskFromEscalation(data)],
      ["置信度", formatConfidence(data.confidence)],
    ],
    sections: [
      { title: "升级摘要", content: data.escalation_summary || data.suggested_summary, type: "text" },
      { title: "建议负责人", content: data.recommended_owner || data.escalation_team, type: "text" },
      { title: "风险等级", content: riskFromEscalation(data), type: "text" },
      { title: "缺失信息", content: firstArray(data.missing_information, data.required_information), type: "list" },
      { title: "临时处理建议", content: data.temporary_workaround || workaroundFromEscalation(data), type: "list" },
      { title: "升级条件", content: data.escalation_criteria, type: "list" },
    ],
  };
}

function normalizeKnowledgeStatus(_, data) {
  return {
    title: "知识库状态报告",
    summaryItems: [
      ["知识库目录", data.knowledge_dir],
      ["当前模式", data.mode],
      ["文档总数", data.document_count],
      ["provider_ready", String(data.provider_ready)],
    ],
    sections: [
      {
        title: "知识库状态",
        content: compactObject({
          knowledge_dir: data.knowledge_dir,
          vector_store: data.vector_store,
          chroma_dir: data.chroma_dir,
          collection: data.collection,
          chunk_size: data.chunk_size,
          chunk_overlap: data.chunk_overlap,
          top_k: data.top_k,
          provider_ready: String(data.provider_ready),
          mode: data.mode,
          document_count: data.document_count,
          active_count: data.active_count,
          deprecated_count: data.deprecated_count,
          draft_count: data.draft_count,
          indexed_status: data.indexed_status,
          message: data.message,
        }),
        type: "kv",
      },
      { title: "支持文件类型", content: data.supported_file_types, type: "list" },
    ],
  };
}

function normalizeKnowledgeVersions(_, data) {
  return {
    title: "文档版本列表",
    summaryItems: [
      ["文档总数", data.document_count],
      ["active 数量", data.active_count],
      ["deprecated 数量", data.deprecated_count],
      ["draft 数量", data.draft_count],
    ],
    sections: [
      { title: "文档版本", content: data.documents || [], type: "records" },
    ],
  };
}

function normalizeKnowledgeReindex(_, data) {
  return {
    title: "知识库重建结果",
    summaryItems: [
      ["状态", data.status],
      ["当前模式", data.mode],
      ["chunk 数量", data.chunk_count],
      ["provider_ready", String(data.provider_ready)],
    ],
    sections: [
      {
        title: "重建结果",
        content: compactObject({
          document_count: data.document_count,
          active_count: data.active_count,
          deprecated_count: data.deprecated_count,
          draft_count: data.draft_count,
          chunk_count: data.chunk_count,
          chunk_size: data.chunk_size,
          chunk_overlap: data.chunk_overlap,
          indexed_status: data.indexed_status,
          message: data.message,
        }),
        type: "kv",
      },
    ],
  };
}

function normalizePreviewChunks(_, data) {
  return {
    title: "文档切分预览",
    summaryItems: [
      ["chunk_size", data.chunk_size],
      ["chunk_overlap", data.chunk_overlap],
      ["chunk 数量", data.chunk_count],
    ],
    sections: [
      { title: "切分结果", content: data.chunks || [], type: "records" },
    ],
  };
}

function normalizeKnowledgeSearch(_, data) {
  return {
    title: "知识库检索测试报告",
    summaryItems: [
      ["当前模式", data.mode],
      ["top_k", data.top_k],
      ["包含历史知识", String(data.include_deprecated)],
      ["结果数量", (data.results || []).length],
    ],
    sections: [
      { title: "检索问题", content: data.query, type: "text" },
      { title: "检索结果", content: data.results || [], type: "records" },
    ],
  };
}

function normalizeKnowledgeDeprecate(_, data) {
  return {
    title: "知识版本状态更新",
    summaryItems: [
      ["doc_id", data.doc_id],
      ["version", data.version],
      ["新状态", data.new_status],
      ["废弃日期", data.deprecated_at],
    ],
    sections: [
      { title: "更新结果", content: data, type: "kv" },
    ],
  };
}

function genericModel(workflowKey, titleText, data) {
  return {
    title: workflows[workflowKey]?.label || "诊断报告",
    summaryItems: [["结果类型", Array.isArray(data) ? "数组" : typeof data]],
    sections: [{ title: titleText, content: data, type: "auto" }],
  };
}

function renderSummaryCard(model) {
  const card = node("section", "result-card result-summary");
  card.appendChild(node("h3", "result-title", "顶部摘要"));
  const grid = node("div", "summary-grid");
  model.summaryItems.filter(([, value]) => hasContent(value)).forEach(([label, value]) => {
    const item = node("div", "summary-item");
    item.appendChild(node("div", "summary-label", label));
    const valueNode = node("div", "summary-value");
    valueNode.appendChild(formatValueNode(value, label));
    item.appendChild(valueNode);
    grid.appendChild(item);
  });
  if (!grid.children.length) {
    grid.appendChild(node("div", "summary-item", "暂无摘要信息"));
  }
  card.appendChild(grid);
  return card;
}

function renderSection(section) {
  const card = node("section", "result-card result-section");
  card.appendChild(node("h3", "result-title", section.title));
  card.appendChild(renderContent(section.content, section.type));
  return card;
}

function renderContent(content, type = "auto") {
  if (!hasContent(content)) return node("div", "result-text-block", "暂无内容");
  if (type === "references") return renderReferences(content);
  if (type === "records") return renderRecords(content);
  if (type === "kv") return renderKeyValues(content);
  if (type === "list" || Array.isArray(content)) return renderList(content);
  if (typeof content === "object") return renderKeyValues(content);
  return node("div", "result-text-block", String(content));
}

function renderRecords(items) {
  const values = Array.isArray(items) ? items : [items];
  const wrapper = node("div", "result-section");
  values.filter(hasContent).forEach((item) => {
    const card = node("div", "result-text-block");
    card.appendChild(renderKeyValues(item));
    wrapper.appendChild(card);
  });
  return wrapper.children.length ? wrapper : node("div", "result-text-block", "暂无记录");
}

function renderKeyValues(obj) {
  const wrapper = node("div", "key-value-list");
  Object.entries(obj || {})
    .filter(([, value]) => hasContent(value))
    .forEach(([key, value]) => {
      const row = node("div", "key-value-row");
      row.appendChild(node("div", "key-name", fieldLabels[key] || key));
      const valueNode = node("div", "key-value");
      valueNode.appendChild(formatValueNode(value, key));
      row.appendChild(valueNode);
      wrapper.appendChild(row);
    });
  return wrapper.children.length ? wrapper : node("div", "result-text-block", "暂无内容");
}

function renderList(items) {
  const values = Array.isArray(items) ? items : [items];
  const list = node("ol", "result-list");
  values.filter(hasContent).forEach((item) => {
    const li = document.createElement("li");
    li.appendChild(formatValueNode(item));
    list.appendChild(li);
  });
  return list.children.length ? list : node("div", "result-text-block", "暂无内容");
}

function renderReferences(items) {
  const refs = Array.isArray(items) ? items : [items];
  const list = node("ol", "result-list");
  refs.filter(hasContent).forEach((ref) => {
    const li = document.createElement("li");
    if (typeof ref === "object") {
      const source = ref.source || ref.file || ref.path || "未提供来源";
      const score = ref.score !== undefined && ref.score !== null ? `，分数：${ref.score}` : "";
      const titleText = ref.title ? `，标题：${ref.title}` : "";
      const preview = ref.content_preview || ref.content || "";
      li.textContent = `${source}${titleText}${score}${preview ? `\n${preview}` : ""}`;
    } else {
      li.textContent = String(ref);
    }
    list.appendChild(li);
  });
  return list.children.length ? list : node("div", "result-text-block", "暂无参考来源");
}

function renderActionCard(rawData) {
  const card = node("section", "result-card");
  const actions = node("div", "result-actions");
  const copyButton = node("button", "copy-button", "复制诊断报告");
  copyButton.type = "button";
  copyButton.addEventListener("click", async () => {
    await copyReport(copyButton);
  });
  actions.appendChild(copyButton);

  ["useful", "not_useful"].forEach((rating) => {
    const button = node("button", `feedback-button ${rating}`, `标记 ${rating}`);
    button.type = "button";
    button.dataset.rating = rating;
    button.addEventListener("click", () => submitFeedback(rating));
    actions.appendChild(button);
  });

  const rawButton = node("button", "raw-json-toggle", rawJsonOpen ? "收起原始 JSON" : "查看原始 JSON");
  rawButton.type = "button";
  actions.appendChild(rawButton);
  card.appendChild(actions);

  const rawPanel = node("div", rawJsonOpen ? "raw-json-panel open" : "raw-json-panel");
  const pre = document.createElement("pre");
  pre.textContent = JSON.stringify(rawData, null, 2);
  rawPanel.appendChild(pre);
  card.appendChild(rawPanel);

  rawButton.addEventListener("click", () => {
    rawJsonOpen = !rawJsonOpen;
    rawPanel.classList.toggle("open", rawJsonOpen);
    rawButton.textContent = rawJsonOpen ? "收起原始 JSON" : "查看原始 JSON";
  });

  return card;
}

async function submitFeedback(rating) {
  if (!lastResult) {
    renderError({ status: "-", message: "请先执行一次分析，再提交反馈。" });
    return;
  }
  const payload = {
    workflow: workflows[currentWorkflow].endpoint.replace("/", ""),
    rating,
    question: JSON.stringify(collectPayload()),
    answer: lastReportText,
    source: "web-console",
  };
  try {
    const feedback = await postJson("/feedback", payload);
    const badge = node("div", "result-card");
    badge.appendChild(node("span", `result-badge ${rating}`, rating));
    badge.appendChild(node("div", "hint", `反馈已保存：${feedback.feedback_file}`));
    result.appendChild(badge);
  } catch (error) {
    renderError(error);
  }
}

async function copyReport(button) {
  const text = lastReportText || "CloudSupport AI 诊断报告\n暂无内容";
  try {
    await navigator.clipboard.writeText(text);
  } catch (_) {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }
  const previous = button.textContent;
  button.textContent = "已复制";
  setTimeout(() => {
    button.textContent = previous;
  }, 1400);
}

function renderError(error) {
  result.innerHTML = "";
  const card = node("section", "error-card");
  card.appendChild(node("h3", "result-title", "请求失败"));
  const status = error.status || "未知";
  card.appendChild(renderKeyValues({
    "HTTP 状态码": status,
    错误信息: error.message || String(error),
    建议: "请检查后端服务是否正常，并确认请求参数是否完整。",
  }));
  result.appendChild(card);
}

function buildReportText(model) {
  const lines = ["CloudSupport AI 诊断报告", ""];
  model.summaryItems.filter(([, value]) => hasContent(value)).forEach(([label, value]) => {
    lines.push(`${label}：${plainText(value)}`);
  });
  model.sections.filter((section) => hasContent(section.content)).forEach((section) => {
    lines.push("", `${section.title}：`);
    appendPlainContent(lines, section.content);
  });
  return lines.join("\n");
}

function appendPlainContent(lines, content) {
  if (Array.isArray(content)) {
    content.filter(hasContent).forEach((item, index) => {
      lines.push(`${index + 1}. ${plainText(item)}`);
    });
    return;
  }
  if (typeof content === "object" && content !== null) {
    Object.entries(content).filter(([, value]) => hasContent(value)).forEach(([key, value]) => {
      lines.push(`${fieldLabels[key] || key}：${plainText(value)}`);
    });
    return;
  }
  lines.push(plainText(content));
}

function formatValueNode(value, key = "") {
  if (Array.isArray(value)) return renderList(value);
  if (typeof value === "object" && value !== null) return renderKeyValues(value);
  const text = String(value);
  if (looksLikeBadge(text, key)) return node("span", badgeClass(text), text);
  return document.createTextNode(text);
}

function looksLikeBadge(text, key) {
  const value = text.toLowerCase();
  return (
    ["priority", "severity", "risk_level", "status_code"].includes(key) ||
    /^p[0-3]$/.test(value) ||
    ["high", "medium", "low", "critical", "useful", "not_useful"].includes(value) ||
    ["active", "deprecated", "draft", "chroma", "keyword_fallback"].includes(value) ||
    /^(401|403|429|500|502|503|504)$/.test(value)
  );
}

function badgeClass(text) {
  const value = String(text).toLowerCase();
  const statusMatch = value.match(/^(401|403|429|500|502|503|504)$/);
  return `result-badge ${statusMatch ? `status-${statusMatch[1]}` : value}`;
}

function firstArray(...values) {
  for (const value of values) {
    if (Array.isArray(value) && value.length) return value;
    if (hasContent(value) && !Array.isArray(value)) return [value];
  }
  return [];
}

function compactObject(obj) {
  return Object.fromEntries(Object.entries(obj).filter(([, value]) => hasContent(value)));
}

function hasContent(value) {
  if (value === null || value === undefined) return false;
  if (Array.isArray(value)) return value.some(hasContent);
  if (typeof value === "object") return Object.values(value).some(hasContent);
  return String(value).trim() !== "";
}

function shortText(value) {
  const text = plainText(value);
  return text.length > 160 ? `${text.slice(0, 160)}...` : text;
}

function plainText(value) {
  if (Array.isArray(value)) return value.map(plainText).join("；");
  if (typeof value === "object" && value !== null) {
    return Object.entries(value)
      .filter(([, item]) => hasContent(item))
      .map(([key, item]) => `${fieldLabels[key] || key}: ${plainText(item)}`)
      .join("；");
  }
  return String(value ?? "");
}

function formatConfidence(value) {
  if (value === null || value === undefined || value === "") return "";
  const number = Number(value);
  if (Number.isNaN(number)) return String(value);
  return number <= 1 ? number.toFixed(2) : String(number);
}

function slaFromPriority(priority) {
  const value = String(priority || "").toLowerCase();
  if (value === "p0") return "立即响应，持续跟进直到恢复";
  if (value === "p1") return "高优先级处理，建议尽快完成首轮定位";
  if (value === "p2") return "常规优先级处理，补齐证据后继续排查";
  return "低优先级或咨询类问题，按常规队列处理";
}

function riskFromEscalation(data) {
  const text = `${data.suggested_summary || ""} ${data.category || ""} ${data.escalation_criteria || ""}`.toLowerCase();
  if (text.includes("multiple users") || text.includes("critical") || text.includes("504") || text.includes("5xx")) {
    return "high";
  }
  if (text.includes("permission") || text.includes("quota") || text.includes("timeout")) return "medium";
  return "low";
}

function workaroundFromEscalation(data) {
  const risk = riskFromEscalation(data);
  if (risk === "high") {
    return ["保留 request ID、时间戳和完整错误响应", "评估是否需要临时降级、重试或切换备用路径", "同步影响范围并保持客户更新节奏"];
  }
  return ["补齐缺失信息后继续排查", "使用最小可复现请求进行对比验证"];
}

function buildApiCustomerSuggestion(data) {
  return [
    "建议先向客户说明当前问题仍在分析中，避免直接下最终结论。",
    data.issue_summary ? `当前观察到：${data.issue_summary}` : "",
    "请客户补充 request ID、时间戳、完整错误响应、请求参数、模型名称或接口路径，以便继续定位。",
  ]
    .filter(Boolean)
    .join("\n");
}

function extractLogSignals(logText) {
  const fields = {};
  ["request_time", "upstream_response_time", "request_id", "error", "status"].forEach((key) => {
    const match = logText.match(new RegExp(`${key}=("[^"]+"|[^\\s]+)`, "i"));
    if (match) fields[key] = match[1].replace(/^"|"$/g, "");
  });
  return fields;
}

function node(tag, className = "", text = "") {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text) element.textContent = text;
  return element;
}

renderNav();
renderFields();
renderEmptyState();
