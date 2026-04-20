from django.urls import path

from . import diagnostics_views, views

app_name = "speech"

urlpatterns = [
    path("attempt/", views.speech_attempt, name="speech-attempt"),
    path("tts/", views.text_to_speech, name="text-to-speech"),
    path("transcribe/", views.transcribe, name="transcribe"),
    path("diagnostics/summary/", diagnostics_views.diagnostics_summary, name="diagnostics-summary"),
    path("diagnostics/phonemes/", diagnostics_views.diagnostics_by_phoneme, name="diagnostics-phonemes"),
    path("diagnostics/daily/", diagnostics_views.diagnostics_daily, name="diagnostics-daily"),
]
