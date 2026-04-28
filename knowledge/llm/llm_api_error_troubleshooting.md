# LLM API Error Troubleshooting

## Scenario

This document applies when a customer receives errors while calling an LLM API endpoint, especially `401 Unauthorized`, `429 Too Many Requests`, or `5xx` server-side errors.

## Symptoms

- API returns `401` with messages such as `invalid api key`, `unauthorized`, or `permission denied`.
- API returns `429` with messages such as `rate limit exceeded`, `quota exceeded`, or `too many requests`.
- API returns `500`, `502`, `503`, or `504` intermittently.
- The same request works locally but fails on a server or CI environment.
- Streaming responses are interrupted by a proxy, gateway, or timeout.

## Possible Causes

- API key is missing, expired, disabled, or loaded from the wrong environment variable.
- The API key does not have access to the selected model, workspace, or endpoint.
- Base URL, model name, API version, or SDK version is incorrect.
- RPM, TPM, QPS, concurrency, billing, or workspace quota has been exceeded.
- Request payload is too large, context length is too long, or retry logic is too aggressive.
- Gateway, proxy, or network timeout interrupts the request.

## Troubleshooting Steps

1. Verify that the API key is loaded in the runtime environment, not only in the local shell.
2. Confirm the base URL, model name, endpoint path, SDK version, and API version.
3. For `401`, test with a minimal request and confirm model permission for the key.
4. For `429`, check RPM, TPM, concurrency, billing status, and workspace quota.
5. Add exponential backoff with jitter for retryable errors.
6. For `5xx`, collect request ID, timestamp, model name, payload size, and retry behavior.
7. Check whether an HTTP proxy, Nginx, gateway, or firewall is interrupting streaming responses.

## Required Information

- HTTP status code and full error response body.
- Request ID or trace ID.
- Timestamp with timezone.
- Model name, endpoint, SDK version, and API version.
- Token usage, input size, output size, and concurrency level.
- Whether the request is streaming or non-streaming.
- Runtime environment, proxy configuration, and retry policy.

## Escalation Criteria

- The API key, quota, endpoint, and model permission are confirmed correct but `401` or `429` persists.
- Multiple regions or environments show consistent `5xx` errors for the same model endpoint.
- The provider returns a request ID that requires backend trace lookup.
- Retry with backoff does not reduce transient failures.
