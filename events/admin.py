from auditlog_extra.mixins import AuditlogAdminViewAccessLogMixin
from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import model_format_dict
from django.contrib.admin.widgets import AdminSplitDateTime, FilteredSelectMultiple
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import BaseInlineFormSet, ModelMultipleChoiceField
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm

from common.mixins import PreDjango6AssumeHttpsURLFieldAdminMixin
from events.ticket_service import check_ticket_validity
from subscriptions.models import FreeSpotNotificationSubscription

from .models import (
    Enrolment,
    Event,
    EventGroup,
    Occurrence,
    TicketSystemPassword,
    validate_registration_opens_at,
)


class RegistrationOpensAtForm(forms.Form):
    registration_opens_at = forms.SplitDateTimeField(
        label=_("registration opens at"), widget=AdminSplitDateTime()
    )

    def clean_registration_opens_at(self):
        registration_opens_at = self.cleaned_data["registration_opens_at"]
        validate_registration_opens_at(registration_opens_at)
        return registration_opens_at


class PublishActionMixin:
    """
    Provide a "publish" admin action, which asks for the registration opening time
    on an intermediate page and passes it to the selected objects' publish().
    """

    publish_help_text = ""

    @admin.action(description=_("Publish selected %(verbose_name_plural)s"))
    def publish(self, request, queryset):
        form = RegistrationOpensAtForm(
            request.POST if "apply" in request.POST else None
        )
        if not form.is_valid():
            return TemplateResponse(
                request,
                "admin/events/publish_with_registration_opens_at.html",
                {
                    **self.admin_site.each_context(request),
                    "title": _("Publish selected %(verbose_name_plural)s")
                    % model_format_dict(self.opts),
                    "opts": self.opts,
                    "queryset": queryset,
                    "form": form,
                    "help_text": self.publish_help_text,
                    "media": self.media + form.media,
                    "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
                },
            )

        success_count = 0
        for obj in queryset:
            try:
                obj.publish(
                    registration_opens_at=form.cleaned_data["registration_opens_at"]
                )
                success_count += 1
            except ValidationError as e:
                self.message_user(request, f"{obj}: {e.message}", level=messages.ERROR)
        if success_count:
            self.message_user(request, _("%s successfully published.") % success_count)
        return None


class BaseBooleanListFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return ("1", _("Yes")), ("0", _("No"))


class IsPublishedFilter(BaseBooleanListFilter):
    title = _("published")
    parameter_name = "is_published"
    lookup_kwarg = "published_at__isnull"

    def queryset(self, request, queryset):
        if self.value() == "0":
            return queryset.filter(**{self.lookup_kwarg: True})
        if self.value() == "1":
            return queryset.filter(**{self.lookup_kwarg: False})


class OccurrenceIsPublishedFilter(IsPublishedFilter):
    lookup_kwarg = "event__published_at__isnull"


class OccurrenceIsUpcomingFilter(BaseBooleanListFilter):
    title = _("upcoming")
    parameter_name = "is_upcoming"

    def queryset(self, request, queryset):
        if self.value() == "0":
            return queryset.in_past()
        if self.value() == "1":
            return queryset.upcoming()


class OccurrencesInline(PreDjango6AssumeHttpsURLFieldAdminMixin, admin.StackedInline):
    model = Occurrence
    extra = 0


@admin.register(Event)
class EventAdminPreDjango6(
    PublishActionMixin, PreDjango6AssumeHttpsURLFieldAdminMixin, TranslatableAdmin
):
    list_display = (
        "id",
        "name",
        "capacity_per_occurrence",
        "participants_per_invite",
        "published_at",
        "registration_opens_at",
        "project",
        "created_at",
        "updated_at",
        "event_group",
        "ready_for_event_group_publishing",
        "ticket_system",
        "ticket_system_url",
        "ticket_system_end_time",
    )
    list_display_links = ("id", "name")
    fields = (
        "project",
        "name",
        "short_description",
        "description",
        "capacity_per_occurrence",
        "participants_per_invite",
        "duration",
        "image",
        "image_alt_text",
        "published_at",
        "registration_opens_at",
        "event_group",
        "ready_for_event_group_publishing",
        "ticket_system",
        "ticket_system_url",
        "ticket_system_end_time",
    )
    search_fields = ("translations__name", "event_group__translations__name")
    inlines = [
        OccurrencesInline,
    ]
    actions = ["publish"]
    publish_help_text = _(
        "The registration opening time is set to each selected event. Already "
        "published events are published again, and guardians are notified again."
    )
    readonly_fields = ("published_at",)
    list_filter = (
        "project",
        ("event_group", admin.RelatedOnlyFieldListFilter),
        IsPublishedFilter,
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "translations",
                "event_group__translations",
                "project__translations",
                "event_group__project",
            )
        )


class EnrolmentsInlineFormSet(BaseInlineFormSet):
    def delete_existing(self, obj, commit=True):
        if commit:
            obj.delete_and_send_notification()


class EnrolmentsInline(admin.TabularInline):
    model = Enrolment
    extra = 0
    fields = (
        "child",
        "attended",
        "created_at",
        "updated_at",
        "reminder_sent_at",
        "feedback_notification_sent_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    formset = EnrolmentsInlineFormSet
    raw_id_fields = ("child",)


class FreeSpotNotificationSubscriptionInline(admin.TabularInline):
    model = FreeSpotNotificationSubscription
    extra = 0
    fields = ("child", "created_at")
    readonly_fields = ("created_at",)
    raw_id_fields = ("child",)


@admin.register(Occurrence)
class OccurrenceAdminPreDjango6(
    AuditlogAdminViewAccessLogMixin,
    PreDjango6AssumeHttpsURLFieldAdminMixin,
    admin.ModelAdmin,
):
    enable_list_view_audit_logging = False  # Not needed in list view
    list_display = (
        "time",
        "event",
        "venue",
        "get_enrolments",
        "get_free_spot_notification_subscriptions",
        "occurrence_language",
        "ticket_system_url",
        "created_at",
        "updated_at",
    )
    fields = (
        "time",
        "event",
        "venue",
        "occurrence_language",
        "capacity_override",
        "ticket_system_url",
    )
    inlines = [EnrolmentsInline, FreeSpotNotificationSubscriptionInline]
    list_filter = (
        "event__project",
        ("event", admin.RelatedOnlyFieldListFilter),
        ("venue", admin.RelatedOnlyFieldListFilter),
        OccurrenceIsPublishedFilter,
        OccurrenceIsUpcomingFilter,
    )
    ordering = ("-time",)
    search_fields = ("event__translations__name",)

    @admin.display(description=_("enrolments"))
    def get_enrolments(self, obj):
        return f"{obj.get_enrolment_count()} / {obj.get_capacity()}"

    @admin.display(description=_("subscriptions"))
    def get_free_spot_notification_subscriptions(self, obj):
        return obj.free_spot_notification_subscriptions.count()

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "event__translations",
                "venue__translations",
                "enrolments",
                "free_spot_notification_subscriptions",
            )
        )


class EventGroupForm(TranslatableModelForm):
    events = ModelMultipleChoiceField(
        queryset=Event.objects.all(),
        widget=FilteredSelectMultiple(verbose_name="events", is_stacked=False),
        required=False,
    )

    class Meta:
        model = EventGroup
        fields = (
            "project",
            "name",
            "short_description",
            "description",
            "image",
            "image_alt_text",
            "published_at",
            "events",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["events"].initial = self.instance.events.all()


@admin.register(EventGroup)
class EventGroupAdmin(PublishActionMixin, TranslatableAdmin):
    list_display = (
        "id",
        "name_with_fallback",
        "short_description_with_fallback",
        "project",
        "get_event_count",
        "published_at",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "name_with_fallback")
    readonly_fields = ("published_at",)
    form = EventGroupForm
    actions = ("publish",)
    publish_help_text = _(
        "On the initial publication of an event group, the registration opening time "
        "is set to all its events. On republication, it is set only to its "
        "unpublished events, and already published events are left unchanged. "
        "Republishing an event group without unpublished events is not allowed."
    )
    list_filter = ("project", IsPublishedFilter)
    search_fields = ("translations__name", "translations__short_description")

    @admin.display(description=_("name"))
    def name_with_fallback(self, obj):
        """By default the current active language is used,
        but if the browser is using some other locale than what is set as a default
        in the Django, then there might be some missing translations,
        because the Kukkuu and Kukkuu Admin UI has been empty string to
        untranslated fields. This uses the ddefault language ("fi") in cases
        when the current active language returns an empty string.

        Args:
            obj (EventGroup): EventGroup model instance

        Returns:
            string: name in the current active language or in Finnish as a fallback
        """
        return obj.safe_translation_getter(
            "name", any_language=True
        ) or obj.safe_translation_getter("name", language_code=settings.LANGUAGE_CODE)

    @admin.display(description=_("short description"))
    def short_description_with_fallback(self, obj):
        """By default the current active language is used,
        but if the browser is using some other locale than what is set as a default
        in the Django, then there might be some missing translations,
        because the Kukkuu and Kukkuu Admin UI has been empty string to
        untranslated fields. This uses the default language ("fi") in cases
        when the current active language returns an empty string.

        Args:
            obj (EventGroup): EventGroup model instance

        Returns:
            string: short description in the current active language
                or in Finnish as a fallback
        """
        return obj.safe_translation_getter(
            "short_description", any_language=True
        ) or obj.safe_translation_getter("name", language_code=settings.LANGUAGE_CODE)

    @admin.display(description=_("event count"))
    def get_event_count(self, obj):
        return obj.events.count()

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        obj.save()
        obj.events.set(form.cleaned_data["events"])

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("translations", "project__translations", "events")
        )


class PasswordAssignedListFilter(BaseBooleanListFilter):
    title = _("assigned")
    parameter_name = "assigned"

    def queryset(self, request, queryset):
        if self.value() == "0":
            return queryset.filter(child=None)
        if self.value() == "1":
            return queryset.exclude(child=None)


@admin.register(TicketSystemPassword)
class TicketSystemChildPasswordAdmin(AuditlogAdminViewAccessLogMixin, admin.ModelAdmin):
    enable_list_view_audit_logging = True
    fields = (
        "value",
        "event",
        "child",
        "assigned_at",
    )
    autocomplete_fields = (
        "child",
        "event",
    )
    list_display = (
        "value",
        "event",
        "child",
        "get_guardian",
        "created_at",
        "assigned_at",
    )
    list_filter = ("event", PasswordAssignedListFilter)
    search_fields = (
        "child__name",
        "child__guardians__first_name",
        "child__guardians__last_name",
        "child__guardians__email",
    )

    @admin.display(description=_("guardian"))
    def get_guardian(self, obj):
        try:
            return obj.child.guardians.all()[0]
        except (AttributeError, IndexError):
            return None

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("child")
            .prefetch_related("child__guardians")
        )


@admin.register(Enrolment)
class EnrolmentAdmin(AuditlogAdminViewAccessLogMixin, admin.ModelAdmin):
    enable_list_view_audit_logging = True
    list_display = (
        "id",
        "child",
        "get_project_year",
        "get_event",
        "occurrence",
        "attended",
        "created_at",
        "reminder_sent_at",
        "feedback_notification_sent_at",
    )
    list_filter = (
        "occurrence__event__project__year",
        "attended",
        "created_at",
        "reminder_sent_at",
        "feedback_notification_sent_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "child",
                    "occurrence",
                    "attended",
                    "created_at",
                    "reminder_sent_at",
                    "feedback_notification_sent_at",
                ],
            },
        ),
        (
            _("Ticket validity"),
            {
                "fields": [
                    "reference_id",
                    "is_reference_id_valid",
                ],
            },
        ),
    )
    search_fields = (
        "child__name",
        "occurrence__event__translations__name",
    )
    autocomplete_fields = [
        "child",
        "occurrence",
    ]
    readonly_fields = [
        "reminder_sent_at",
        "feedback_notification_sent_at",
        "created_at",
        "reference_id",
        "is_reference_id_valid",
    ]
    date_hierarchy = "created_at"
    order = "-created_at"

    @admin.display(description=_("event"))
    def get_event(self, obj: Enrolment):
        return obj.occurrence.event

    @admin.display(description=_("project year"))
    def get_project_year(self, obj: Enrolment):
        return obj.occurrence.event.project.year

    @admin.display(description=_("reference id validity"))
    def is_reference_id_valid(self, obj: Enrolment):
        _, is_valid = check_ticket_validity(obj.reference_id)
        return is_valid
