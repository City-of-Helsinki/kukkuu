from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import Event, Occurrence


class OccurrencesInline(admin.StackedInline):
    model = Occurrence
    extra = 1


@admin.register(Event)
class EventAdmin(TranslatableAdmin):
    list_display = (
        "id",
        "name",
        "short_description",
        "duration",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "name")
    fields = ("name", "short_description", "description", "duration")
    inlines = [
        OccurrencesInline,
    ]


@admin.register(Occurrence)
class OccurrenceAdmin(admin.ModelAdmin):
    list_display = ("id", "time", "event", "created_at", "updated_at")
    list_display_links = ("id", "time")
    fields = ("time", "event", "venue")
