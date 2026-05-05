# Prompt Optimization

## Scenario

适用于 AI 支持助手输出格式不稳定、回答不够克制、缺少排查步骤或客户回复语气不合适的场景。

## Symptoms

- 输出结构不统一。
- 缺少可能原因、排查步骤或需要补充的信息。
- 在证据不足时给出确定结论。

## Possible Causes

- Prompt 没有明确角色、任务和输出格式。
- 没有限制模型基于上下文回答。
- Temperature 过高或示例不稳定。
- 缺少“不足以确认时如何回答”的约束。

## Troubleshooting Steps

1. 明确角色和任务边界。
2. 固定输出字段和格式。
3. 增加禁止编造、证据不足和升级条件规则。
4. 使用典型案例回归测试 Prompt。
5. 对客户回复单独定义语气和下一步动作。

## Required Information

- 原始 Prompt
- 输入样例和输出样例
- 期望输出格式
- 失败案例和业务风险

## Escalation Criteria

- Prompt 调整后仍无法稳定满足结构化输出。
- 输出涉及高风险业务结论或合规内容。
