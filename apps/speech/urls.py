from django.urls import path

from . import views

app_name = "speech"

urlpatterns = [
    path("attempt/", views.speech_attempt, name="speech-attempt"),
    path("tts/", views.text_to_speech, name="text-to-speech"),
]
