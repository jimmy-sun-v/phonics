import logging
from dataclasses import dataclass

from django.conf import settings

from apps.speech.logging_config import log_service_call

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    text: str
    is_successful: bool
    error_message: str | None = None


@log_service_call("azure_llm")
def call_llm(messages: list[dict[str, str]]) -> LLMResponse:
    from openai import AzureOpenAI

    api_key = settings.AZURE_OPENAI_KEY
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    deployment = settings.AZURE_OPENAI_DEPLOYMENT

    if not api_key or not endpoint:
        logger.error("Azure OpenAI credentials not configured")
        return LLMResponse(text="", is_successful=False, error_message="AI service not configured")

    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version="2024-06-01",
            azure_endpoint=endpoint,
        )

        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_tokens=100,
            temperature=0.3,
            top_p=0.9,
            timeout=10,
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
        return LLMResponse(text="", is_successful=False, error_message=str(e))
