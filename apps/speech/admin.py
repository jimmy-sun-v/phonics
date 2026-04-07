from django.contrib import admin

from .models import SpeechAttempt


@admin.register(SpeechAttempt)
class SpeechAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "phoneme", "confidence", "detected_error", "attempt_number", "created_at")
    list_filter = ("phoneme__category",)
    readonly_fields = ("created_at",)
    search_fields = ("session__session_id",)
