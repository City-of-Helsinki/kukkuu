from django.contrib import admin
from parler.admin import TranslatableAdmin

from events.admin import OccurrencesInline
from venues.models import Venue


@admin.register(Venue)
class VenueAdmin(TranslatableAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    list_display_links = ("id", "name")
    exclude = ("id", "created_at", "updated_at")

    inlines = [
        OccurrencesInline,
    ]
