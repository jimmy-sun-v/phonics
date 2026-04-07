import logging
from apps.speech.logging_config import log_service_call


def test_log_service_call_success(caplog):
    @log_service_call("test_service")
    def my_func():
        return "ok"

    with caplog.at_level(logging.INFO, logger="phonics.speech"):
        result = my_func()

    assert result == "ok"
    assert "service_call" in caplog.text


def test_log_service_call_error(caplog):
    @log_service_call("test_service")
    def my_func():
        raise ValueError("test error")

    with caplog.at_level(logging.ERROR, logger="phonics.speech"):
        try:
            my_func()
        except ValueError:
            pass

    assert "service_call_error" in caplog.text
