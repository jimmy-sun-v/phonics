from unittest.mock import MagicMock, patch

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
