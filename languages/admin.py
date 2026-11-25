from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from parler.utils.context import switch_language

from .forms import LivingLanguageSearchForm
from .models import InvalidLanguageCodeError, Language, LanguageAlreadyExistsError
from .search import search_living_languages

LIVING_LANGUAGE_SEARCH_PAGE_SIZE = 50


@admin.register(Language)
class LanguageAdmin(TranslatableAdmin):
    change_list_template = "admin/languages/language/change_list.html"
    list_display = (
        "alpha_3_code",
        "get_name_fi",
        "get_name_sv",
        "get_name_en",
        "can_be_spoken_at_home",
        "can_be_occurrence_language",
        "get_guardian_count",
    )
    list_display_links = ("alpha_3_code", "get_name_fi", "get_name_sv", "get_name_en")
    list_filter = ("can_be_spoken_at_home", "can_be_occurrence_language")
    search_fields = ("alpha_3_code", "translations__name")
    fields = (
        "alpha_3_code",
        "name",
        "can_be_spoken_at_home",
        "can_be_occurrence_language",
        "get_guardian_count",
    )
    readonly_fields = ("get_guardian_count",)

    def get_urls(self):
        add_living_urls = [
            path(
                "add-living/",
                self.admin_site.admin_view(self.add_living_view),
                name="languages_language_add_living",
            ),
        ]
        return add_living_urls + super().get_urls()

    def add_living_view(self, request):
        """
        Show a page for searching the living ISO 639-3 languages and adding one of
        them. On POST, add the chosen language.
        """
        if not self.has_add_permission(request):
            raise PermissionDenied

        if request.method == "POST":
            return self._add_living_language(request, request.POST.get("code", ""))

        form = LivingLanguageSearchForm(request.GET or None)
        page = None
        existing_codes = set()
        if form.is_valid():
            languages = search_living_languages(form.cleaned_data["search_term"])
            paginator = Paginator(languages, LIVING_LANGUAGE_SEARCH_PAGE_SIZE)
            page = paginator.get_page(request.GET.get("page"))
            existing_codes = set(
                Language.objects.filter(
                    alpha_3_code__in=[language.alpha_3 for language in page]
                ).values_list("alpha_3_code", flat=True)
            )

        return TemplateResponse(
            request,
            "admin/languages/language/add_living.html",
            {
                **self.admin_site.each_context(request),
                "title": _("Add language from living world languages list"),
                "form": form,
                "page": page,
                "existing_codes": existing_codes,
            },
        )

    def _add_living_language(self, request, code):
        try:
            created = Language.objects.create_from_language_code(
                code, use_english_fallback=True
            )
        except InvalidLanguageCodeError as error:
            return self._report_add_failed(request, str(error))
        except LanguageAlreadyExistsError:
            message = _('Language "%(code)s" already exists.') % {"code": code}
            return self._report_add_failed(request, message)

        self._report_added(request, created)
        return redirect(
            reverse("admin:languages_language_change", args=(created.language.pk,))
        )

    def _report_add_failed(self, request, message):
        self.message_user(request, message, messages.ERROR)
        return redirect("admin:languages_language_add_living")

    def _report_added(self, request, created):
        message = _('Added language "%(language)s".') % {"language": created.language}
        self.message_user(request, message, messages.SUCCESS)

        if created.fallback_language_codes:
            message = _(
                "The English name was used for %(language_codes)s translations "
                "because no translation was found."
            ) % {"language_codes": ", ".join(created.fallback_language_codes)}
            self.message_user(request, message, messages.WARNING)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("translations")
            .translated()
            .annotate(Count("guardians", distinct=True))
            .with_is_special_language()
            .order_by("-is_special_language", "alpha_3_code")  # special languages first
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
