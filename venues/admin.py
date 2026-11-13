from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from events.admin import OccurrencesInline
from venues.models import Venue


@admin.register(Venue)
class VenueAdmin(TranslatableAdmin):
    list_display = (
        "id",
        "name",
        "get_project_year",
        "is_system",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "name")
    list_filter = ("project", "is_system", "created_at", "updated_at")
    list_select_related = ("project",)
    date_hierarchy = "created_at"
    search_fields = ("translations__name",)
    readonly_fields = ("is_system",)
    exclude = ("id", "created_at", "updated_at")

    inlines = [
        OccurrencesInline,
    ]

    @admin.display(description=_("project"))
    def get_project_year(self, obj):
        return obj.project.year if obj.project else "-"

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)
