from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from languages.models import Language
from subscriptions.models import FreeSpotNotificationSubscription

from events.models import Enrolment

from .models import Child, Relationship


class RelationshipInline(admin.TabularInline):
    model = Relationship
    extra = 0
    fields = ("guardian", "type", "created_at")
    readonly_fields = ("created_at",)
    raw_id_fields = ("guardian",)

    def has_change_permission(self, request, obj=None):
        return False


class EnrolmentInline(admin.TabularInline):
    model = Enrolment
    extra = 0
    readonly_fields = ("created_at",)


class LanguagesSpokenAtHomeInline(admin.TabularInline):
    model = Language.children.through
    extra = 0
    verbose_name = _("Language spoken at home")
    verbose_name_plural = _("Languages spoken at home")


class SubscriptionInline(admin.TabularInline):
    model = FreeSpotNotificationSubscription
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "birthdate",
        "postal_code",
        "get_project",
        "get_guardian",
        "created_at",
        "updated_at",
    )
    fields = ("project", "first_name", "last_name", "birthdate", "postal_code")
    search_fields = (
        "first_name",
        "last_name",
        "birthdate",
        "guardians__first_name",
        "guardians__last_name",
        "guardians__email",
    )
    inlines = (
        RelationshipInline,
        EnrolmentInline,
        LanguagesSpokenAtHomeInline,
        SubscriptionInline,
    )
    list_filter = ("project",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("project")
            .prefetch_related("guardians")
        )

    def get_guardian(self, obj):
        try:
            return obj.guardians.all()[0]
        except IndexError:
            return None

    get_guardian.short_description = _("guardian")

    def get_project(self, obj):
        return obj.project.year

    get_project.short_description = _("project")
