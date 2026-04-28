# Function Calling Error Troubleshooting

## Scenario

This document applies when Function Calling or Tool Calling returns invalid arguments, misses required fields, fails schema validation, or does not trigger the expected tool.

## Symptoms

- The model returns JSON that cannot pass schema validation.
- Required fields such as `order_id`, `action_type`, or `user_id` are missing.
- Field types are incorrect, for example string instead of number or object instead of array.
- Enum values do not match the allowed schema values.
- The model responds in natural language instead of calling the tool.
- Error rate increases for complex or deeply nested schemas.

## Possible Causes

- The JSON schema is too complex or deeply nested.
- Field descriptions are vague and do not explain business meaning, allowed values, or units.
- Required fields cannot be inferred from the user input.
- Too many similar enum values confuse the model.
- The prompt does not clearly state when the tool should be called.
- Server-side validation does not provide a repair retry path.

## Troubleshooting Steps

1. Simplify the schema and reduce nesting where possible.
2. Add clear descriptions for each field, including type, unit, allowed values, and examples.
3. Keep enum values short, distinct, and business-readable.
4. In the system prompt, define when the model must call the tool and what to do when information is missing.
5. Validate tool arguments on the server side before executing any business operation.
6. If validation fails, send the validation error back to the model for one repair attempt.
7. Add guardrails for high-risk actions, such as confirmation steps or allowlists.

## Required Information

- Full function/tool schema.
- User input and conversation context.
- Raw model output or tool call payload.
- Schema validation error message.
- Model name, SDK version, and request parameters.
- Whether strict schema mode or parallel tool calls are enabled.

## Escalation Criteria

- The schema is simple and clear, but invalid arguments are consistently returned.
- Strict schema mode still returns invalid payloads.
- Tool calling behavior differs from documented API behavior.
- The invalid tool call may trigger high-risk business operations.
