# Design: Task 7.2 – Azure Speech Services Provisioning

## Overview

Provision Azure Cognitive Services Speech resource and configure the Django application to connect to it for STT and TTS.

## Dependencies

- Task 7.0 (Bicep IaC — Speech Services resource provisioned)
- Task 7.1 (Azure App Service)

> **Note:** Speech Services resource provisioning and key injection into App Settings are handled by the Bicep templates in Task 7.0 (`infra/modules/speech.bicep`). This task documents the resource configuration, quotas, and validation steps.

## Detailed Design

### Resource Provisioning (handled by Task 7.0)

The Speech Services resource is declared in `infra/modules/speech.bicep` and deployed automatically. The API key is wired into the App Service settings by `infra/modules/app-service.bicep`.

| Setting | Value |
|---------|-------|
| Kind | SpeechServices |
| SKU | F0 (free: 5h STT, 0.5M TTS chars/month) or S0 for production |
| Region | Match App Service region |

### Environment Configuration (handled by Task 7.0)

The following App Settings are automatically set by Bicep during deployment:

```
AZURE_SPEECH_KEY=<auto-injected from Bicep output>
AZURE_SPEECH_REGION=<matches deployment region>
```

No manual CLI configuration is needed.

### Network Security

- Enable Virtual Network integration if using private endpoints
- For basic setup, Speech Services accepts public API calls authenticated by key
- Keys are stored as App Service settings (encrypted at rest)

### Quota Monitoring

| SKU | STT Limit | TTS Limit |
|-----|-----------|-----------|
| F0 | 5 hours/month | 0.5M chars/month |
| S0 | Pay-as-you-go | Pay-as-you-go |

Set up Azure Monitor alert for quota approaching 80%:
```bash
az monitor metrics alert create \
    --name speech-quota-warning \
    --resource-group rg-phonics-app \
    --scopes /subscriptions/.../speech-phonics-tutor \
    --condition "total TransactionsCount > 4000" \
    --description "Speech API approaching quota"
```

### Validation

```bash
# Test STT connectivity from App Service
az webapp ssh --name phonics-tutor-app --resource-group rg-phonics-app

# In SSH:
python -c "
import os
import azure.cognitiveservices.speech as speechsdk
config = speechsdk.SpeechConfig(
    subscription=os.environ['AZURE_SPEECH_KEY'],
    region=os.environ['AZURE_SPEECH_REGION']
)
print('Speech config created successfully')
"
```

## Acceptance Criteria

- [ ] Speech Services resource provisioned
- [ ] Keys configured as App Service settings
- [ ] STT works from deployed app (test via speech attempt)
- [ ] TTS works from deployed app (test via TTS endpoint)
- [ ] Monitoring alert configured for quota

## Test Strategy

- Manual: Deploy → make speech attempt → verify STT+TTS work
- Manual: Check Azure Portal → Speech resource → metrics
- Manual: Verify keys are not in source code
