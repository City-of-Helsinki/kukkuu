from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from parler.admin import TranslatableAdmin

from events.admin import OccurrencesInline
from venues.models import Venue


@admin.register(Venue)
class VenueAdmin(TranslatableAdmin):
    list_display = ("id", "name", "get_project_year", "created_at", "updated_at")
    list_display_links = ("id", "name")
    list_select_related = ("project",)
    exclude = ("id", "created_at", "updated_at")

    inlines = [
        OccurrencesInline,
    ]

    def get_project_year(self, obj):
        return obj.project.year

    get_project_year.short_description = _("project")
