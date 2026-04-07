from django.contrib import admin

from .models import Phoneme


@admin.register(Phoneme)
class PhonemeAdmin(admin.ModelAdmin):
    list_display = ("symbol", "category", "display_order")
    list_filter = ("category",)
    search_fields = ("symbol",)
    ordering = ("category", "display_order")
    list_editable = ("display_order",)
