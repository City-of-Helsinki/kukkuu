from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm

from .models import ThemePath


class ThemePathForm(TranslatableModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if self.language_code != "fi" and (
            self.instance._state.adding or not self.instance.has_translation("fi")
        ):
            raise ValidationError(_("A Finnish translation is required."))
        return cleaned_data


@admin.register(ThemePath)
class ThemePathAdmin(TranslatableAdmin):
    form = ThemePathForm
    list_display = (
        "slug",
        "name",
        "all_languages_column",
        "sort_order",
        "get_event_count",
    )
    list_display_links = ("slug", "name")
    fields = ("slug", "name", "description", "sort_order")
    search_fields = ("slug", "translations__name")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("translations")
            .annotate(Count("events", distinct=True))
        )

    def get_readonly_fields(self, request, obj=None):
        return ("slug",) if obj else ()

    def delete_translation(self, request, object_id, language_code):
        if language_code == "fi":
            self.message_user(
                request, _("The Finnish translation can't be deleted."), messages.ERROR
            )
            return HttpResponseRedirect(
                reverse("admin:tags_themepath_change", args=[object_id])
            )
        return super().delete_translation(request, object_id, language_code)

    @admin.display(description=_("Event count"))
    def get_event_count(self, obj):
        return obj.events__count
