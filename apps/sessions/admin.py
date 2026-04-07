from django.contrib import admin

from .models import LearningSession


@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "current_phoneme", "started_at", "last_active_at", "is_active")
    list_filter = ("is_active", "started_at")
    readonly_fields = ("session_id", "started_at", "last_active_at")
    search_fields = ("session_id",)
