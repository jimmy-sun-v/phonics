from django.contrib import admin

from .models import Game, GamePhonemeMapping


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
