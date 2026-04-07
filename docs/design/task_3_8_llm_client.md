# Design: Task 3.8 – AI Tutor – Azure OpenAI Integration Service

## Overview

Create a service that sends rendered prompt messages to Azure OpenAI and returns the LLM response text, with configured safety parameters.

## Dependencies

- Task 1.7 (Azure OpenAI key in environment)
- Task 3.7 (Prompt rendering service)

## Detailed Design

### Service Module

**File: `apps/ai_tutor/llm_client.py`**

```python
import logging
from dataclasses import dataclass
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    text: str
    is_successful: bool
    error_message: str | None = None


def call_llm(messages: list[dict[str, str]]) -> LLMResponse:
    """Send messages to Azure OpenAI and return the response.

    Args:
        messages: List of message dicts with "role" and "content" keys.
            Expected format: [{"role": "system", ...}, {"role": "user", ...}]

    Returns:
        LLMResponse with generated text or error details.
    """
    from openai import AzureOpenAI

    api_key = settings.AZURE_OPENAI_KEY
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    deployment = settings.AZURE_OPENAI_DEPLOYMENT

    if not api_key or not endpoint:
        logger.error("Azure OpenAI credentials not configured")
        return LLMResponse(
            text="",
            is_successful=False,
            error_message="AI service not configured",
        )

    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version="2024-06-01",
            azure_endpoint=endpoint,
        )

        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_tokens=100,       # Short responses only (1-2 sentences)
            temperature=0.3,      # Low temp for consistency
            top_p=0.9,
            timeout=10,           # 10-second timeout
        )

        text = response.choices[0].message.content.strip()
        logger.info(
            "LLM response generated (%d tokens, model=%s)",
            response.usage.completion_tokens if response.usage else 0,
            deployment,
        )
        return LLMResponse(text=text, is_successful=True)

    except Exception as e:
        logger.exception("Azure OpenAI call failed")
        return LLMResponse(
            text="",
            is_successful=False,
            error_message=str(e),
        )
```

### Configuration

In `config/settings/base.py` (from Task 1.7):
```python
AZURE_OPENAI_KEY = env("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = env("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = env("AZURE_OPENAI_DEPLOYMENT")
```

### LLM Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `max_tokens` | 100 | Enforces 1-2 sentence responses |
| `temperature` | 0.3 | Low randomness for consistent, predictable feedback |
| `top_p` | 0.9 | Slight diversity while maintaining safety |
| `timeout` | 10s | Prevent hanging; overall target is < 1.5s total |

### Error Handling

| Scenario | Behavior |
|----------|----------|
| Missing credentials | Return error LLMResponse |
| API timeout | Exception caught → LLMResponse with error |
| Rate limiting (429) | Exception caught → LLMResponse with error |
| Content filter triggered | Exception caught → LLMResponse with error |
| Success | Return text response |

The caller (Task 3.9 validator) decides whether to use a fallback message.

## Acceptance Criteria

- [ ] Service calls Azure OpenAI with correct endpoint/key
- [ ] `max_tokens` capped at 100
- [ ] `temperature` set to 0.3
- [ ] Timeout of 10 seconds configured
- [ ] Missing credentials → structured error, no crash
- [ ] API errors → structured error, no unhandled exceptions

## Test Strategy

**File: `apps/ai_tutor/tests/test_llm_client.py`**

```python
import pytest
from unittest.mock import patch, MagicMock
from apps.ai_tutor.llm_client import call_llm


class TestLLMClient:
    @patch("apps.ai_tutor.llm_client.settings")
    def test_missing_credentials(self, mock_settings):
        mock_settings.AZURE_OPENAI_KEY = ""
        mock_settings.AZURE_OPENAI_ENDPOINT = ""
        mock_settings.AZURE_OPENAI_DEPLOYMENT = ""
        result = call_llm([{"role": "system", "content": "Hi"}])
        assert result.is_successful is False
        assert "not configured" in result.error_message

    @patch("openai.AzureOpenAI")
    @patch("apps.ai_tutor.llm_client.settings")
    def test_successful_call(self, mock_settings, mock_client_cls):
        mock_settings.AZURE_OPENAI_KEY = "key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT = "gpt-4o-mini"

        mock_choice = MagicMock()
        mock_choice.message.content = "Great try! The 'sh' sound is like a whisper."
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage.completion_tokens = 12

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_client_cls.return_value = mock_client

        messages = [
            {"role": "system", "content": "You are a tutor."},
            {"role": "user", "content": "Practice sh"},
        ]
        result = call_llm(messages)
        assert result.is_successful is True
        assert "sh" in result.text

        # Verify parameters
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["max_tokens"] == 100
        assert call_args.kwargs["temperature"] == 0.3

    @patch("openai.AzureOpenAI")
    @patch("apps.ai_tutor.llm_client.settings")
    def test_api_error_handled(self, mock_settings, mock_client_cls):
        mock_settings.AZURE_OPENAI_KEY = "key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT = "gpt-4o-mini"

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Connection timeout")
        mock_client_cls.return_value = mock_client

        result = call_llm([{"role": "user", "content": "test"}])
        assert result.is_successful is False
        assert "timeout" in result.error_message.lower()
```
