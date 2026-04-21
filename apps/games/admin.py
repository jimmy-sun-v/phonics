from django.contrib import admin
from django.utils.html import escape

from .models import Game, GamePhonemeMapping, StorySession


class GamePhonemeMappingInline(admin.TabularInline):
    model = GamePhonemeMapping
    extra = 1


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "game_type", "is_active")
    list_filter = ("game_type", "is_active")
    search_fields = ("name",)
    inlines = [GamePhonemeMappingInline]


@admin.register(GamePhonemeMapping)
class GamePhonemeMappingAdmin(admin.ModelAdmin):
    list_display = ("game", "phoneme")
    list_filter = ("game__game_type",)


@admin.register(StorySession)
class StorySessionAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "is_complete", "created_at", "short_summary")
    list_filter = ("is_complete", "created_at")
    search_fields = ("summary",)
    readonly_fields = ("created_at",)

    @admin.display(description="Summary")
    def short_summary(self, obj):
        text = obj.summary or ""
        return escape(text[:80]) + ("…" if len(text) > 80 else "")
