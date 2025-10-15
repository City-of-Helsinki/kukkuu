from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from parler.utils.context import switch_language

from .models import Language


@admin.register(Language)
class LanguageAdmin(TranslatableAdmin):
    list_display = (
        "alpha_3_code",
        "get_name_fi",
        "get_name_sv",
        "get_name_en",
        "get_guardian_count",
    )
    list_display_links = ("alpha_3_code", "get_name_fi", "get_name_sv", "get_name_en")
    fields = ("alpha_3_code", "name", "get_guardian_count")
    readonly_fields = ("get_guardian_count",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("translations")
            .translated()
            .annotate(Count("guardians"))
            .annotate(has_code=Count("alpha_3_code"))  # to order null codes as first
            .order_by("has_code", "translations__name", "id")
        )

    @admin.display(description=_("Finnish"))
    def get_name_fi(self, obj):
        with switch_language(obj, "fi"):
            return obj.name

    @admin.display(description=_("Swedish"))
    def get_name_sv(self, obj):
        with switch_language(obj, "sv"):
            return obj.name

    @admin.display(description=_("English"))
    def get_name_en(self, obj):
        with switch_language(obj, "en"):
            return obj.name

    @admin.display(description=_("Guardian count"))
    def get_guardian_count(self, obj):
        return obj.guardians__count
