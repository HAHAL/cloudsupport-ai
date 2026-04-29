# Customer Reply Examples

## API Key Authentication Failure

Dear Customer,

Thank you for contacting us.

Based on the error response, the request appears to be failing during authentication. To continue the investigation, could you please provide the request ID, timestamp with timezone, sanitized request headers, model name, endpoint, and SDK version?

As a quick check, please verify that the API key is correctly loaded in the runtime environment and that the key has permission to access the selected model.

Best regards,  
Technical Support Team

## 429 Rate Limit

Dear Customer,

The error indicates that the request may have reached a rate limit or quota limit. Please provide the affected time range, peak QPS, RPM, TPM, concurrency level, model name, workspace, and full error response body.

As a temporary mitigation, please reduce concurrency and add retry with exponential backoff and jitter.

Best regards,  
Technical Support Team

## Timeout

Dear Customer,

The timeout may be related to request size, model inference latency, network path, or gateway timeout settings. Could you please provide the request ID, timestamp, input token size, output token size, max_tokens setting, and whether streaming is enabled?

You may temporarily reduce prompt length or max output tokens and increase client timeout where appropriate.

Best regards,  
Technical Support Team

## RAG Answer Inaccuracy

Dear Customer,

RAG answer quality usually needs to be checked from both retrieval and prompt constraints. Please provide the original question, expected knowledge document, actual Top-K retrieved chunks, chunk_size, chunk_overlap, Top-K, embedding model, and metadata filters.

We will review whether the issue is caused by recall, ranking, outdated knowledge, or insufficient prompt constraints.

Best regards,  
Technical Support Team

## Escalation Required

Dear Customer,

Based on the current information, this issue may require further investigation by a specialized support or engineering team. Before escalation, please provide the request ID, timestamp with timezone, region, sanitized request body, response body, reproduction steps, and business impact.

Once we receive the information, we will prepare a clear issue summary and continue the investigation.

Best regards,  
Technical Support Team
