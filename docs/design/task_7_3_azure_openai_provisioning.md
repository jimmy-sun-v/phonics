# Design: Task 7.3 – Azure OpenAI Provisioning

## Overview

Provision Azure OpenAI (via AI Foundry) resource and deploy a `gpt-4o-mini` model for generating child-friendly phonics feedback.

## Dependencies

- Task 7.0 (Bicep IaC — OpenAI resource + model deployment provisioned)
- Task 7.1 (Azure App Service)

> **Note:** OpenAI resource provisioning, model deployment, and key injection into App Settings are handled by the Bicep templates in Task 7.0 (`infra/modules/openai.bicep`). This task documents model configuration, content filtering, rate limits, and validation.

## Detailed Design

### Resource Provisioning (handled by Task 7.0)

The Azure OpenAI resource and `gpt-4o-mini` model deployment are declared in `infra/modules/openai.bicep`. The endpoint and API key are wired into App Service settings by `infra/modules/app-service.bicep`.

### Environment Configuration (handled by Task 7.0)

The following App Settings are automatically set by Bicep during deployment:

```
AZURE_OPENAI_ENDPOINT=<auto-injected from Bicep output>
AZURE_OPENAI_API_KEY=<auto-injected from Bicep output>
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-06-01
```

No manual CLI configuration is needed.

### Model Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `max_tokens` | 100 | Short, child-friendly responses |
| `temperature` | 0.3 | Consistent, predictable output |
| `top_p` | 0.9 | Slightly creative but controlled |
| Deployment capacity | 10K TPM | Sufficient for MVP usage |

### Content Filtering

Azure OpenAI includes built-in content filtering. Verify default filters are enabled:
- Hate: Medium
- Sexual: Medium
- Violence: Medium
- Self-harm: Medium

These act as an additional safety layer beyond our application-level `validate_llm_response()`.

### Rate Limiting

| SKU | Tokens per Minute | Requests per Minute |
|-----|-------------------|---------------------|
| Standard (10 capacity) | 10,000 TPM | ~60 RPM |

For MVP this is sufficient. Scale capacity units as needed.

### Validation

```bash
# Test from App Service SSH
python -c "
import os
from openai import AzureOpenAI
client = AzureOpenAI(
    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'],
    api_key=os.environ['AZURE_OPENAI_API_KEY'],
    api_version=os.environ['AZURE_OPENAI_API_VERSION'],
)
resp = client.chat.completions.create(
    model=os.environ['AZURE_OPENAI_DEPLOYMENT'],
    messages=[
        {'role': 'system', 'content': 'You are a helpful phonics tutor.'},
        {'role': 'user', 'content': 'Say hi'},
    ],
    max_tokens=50,
)
print(resp.choices[0].message.content)
"
```

### Cost Estimation (MVP)

- gpt-4o-mini: ~$0.15/1M input tokens, ~$0.60/1M output tokens
- Estimated MVP usage: ~10K requests/month × 200 tokens avg = ~2M tokens
- Estimated cost: < $2/month

## Acceptance Criteria

- [ ] Azure OpenAI resource provisioned
- [ ] gpt-4o-mini model deployed
- [ ] Keys configured as App Service settings (not in code)
- [ ] LLM feedback works from deployed app
- [ ] Content filtering enabled
- [ ] Rate limits documented

## Test Strategy

- Manual: Deploy → make speech attempt → verify LLM feedback returned
- Manual: Check Azure Portal → OpenAI → deployments → gpt-4o-mini active
- Manual: Verify content filtering is enabled in Azure Portal
- Manual: Send test prompt from App Service SSH
