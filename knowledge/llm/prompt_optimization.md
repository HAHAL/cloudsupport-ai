# Prompt Optimization Support Guide

## Scenario

This document applies when an LLM response is unstable, does not follow the required format, ignores constraints, produces unsupported facts, or fails to behave consistently in a support workflow.

## Symptoms

- The model does not return valid JSON or does not follow the expected schema.
- The answer includes facts that are not present in the provided context.
- Small input changes lead to large output differences.
- The model ignores role instructions or output constraints.
- The prompt is long, but key requirements are not followed.
- The response is too verbose, too short, or not suitable for customer-facing support.

## Possible Causes

- System instructions, user instructions, and context contain conflicting requirements.
- Output format requirements are vague or do not include a schema.
- The prompt contains too much unrelated context.
- RAG context is noisy, outdated, or not relevant to the user question.
- Temperature is too high for a deterministic support task.
- There is no server-side JSON validation or retry strategy.

## Troubleshooting Steps

1. Split the prompt into role, task, constraints, input, and output format sections.
2. Clearly state that the model must return only valid JSON when structured output is required.
3. Provide field descriptions and a minimal example for complex schemas.
4. Remove repeated, conflicting, or unrelated context from the prompt.
5. Lower temperature for factual support answers and structured output tasks.
6. Add server-side JSON parsing, schema validation, and a repair retry when validation fails.
7. Define how the model should respond when evidence is insufficient.

## Required Information

- Full prompt template, including system and user messages.
- Input example and unexpected output example.
- Model name, temperature, max tokens, and SDK version.
- Whether RAG context is used and what context was retrieved.
- Expected JSON schema or business validation rules.

## Escalation Criteria

- The prompt is clear and minimal, but the model consistently violates the format.
- Structured output or Function Calling fails with a simple schema.
- The same prompt behavior changes significantly after a model or SDK update.
- The issue affects customer-facing support replies or automated support workflows.
