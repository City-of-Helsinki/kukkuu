from typing import Optional, Tuple

import markdown
from auditlog_extra.mixins import AuditlogAdminViewAccessLogMixin
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from guardian.admin import GuardedModelAdmin

from children.models import Relationship
from languages.models import Language
from projects.models import Project
from reports.models import Permission as ReportPermission
from users.models import Guardian
from users.services import AuthServiceNotificationService

USER_AUTH_SERVICE_IS_CHANGING_NOTIFICATION_TEMPLATE = """
{subject}

{body_text}
""".strip()


class RelationshipInline(admin.TabularInline):
    model = Relationship
    extra = 0
    fields = ("child", "type", "created_at")
    readonly_fields = ("created_at",)

    def has_change_permission(self, request, obj=None):
        return False


class GuardianForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["language"] = forms.ChoiceField(choices=settings.LANGUAGES)


class LanguagesSpokenAtHomeInline(admin.TabularInline):
    model = Language.guardians.through
    extra = 0
    verbose_name = _("Language spoken at home")
    verbose_name_plural = _("Languages spoken at home")


def _generate_children_event_history_markdown(
    modeladmin, request, queryset
) -> Optional[Tuple[Guardian, str]]:
    if queryset.count() != 1:
        modeladmin.message_user(
            request,
            "Only 1 guardian can be selected for "
            "'Generate authorization server is changing notification text' action.",
        )
        return
    guardian = queryset.first()
    return (
        guardian,
        AuthServiceNotificationService.generate_children_event_history_markdown(
            guardian=guardian
        ),
    )


@admin.action(description="Generate children event history markdown")
def generate_children_event_history_markdown(modeladmin, request, queryset):
    (
        guardian,
        children_event_history_markdown,
    ) = _generate_children_event_history_markdown(modeladmin, request, queryset)
    # Use markdown rendered to render this admin view,
    # so the actual end result can be validated.
    return HttpResponse(markdown.markdown(children_event_history_markdown))


@admin.register(Guardian)
class GuardianAdmin(AuditlogAdminViewAccessLogMixin, admin.ModelAdmin):
    enable_list_view_audit_logging = True
    list_display = (
        "id",
        "user_link",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "language",
        "created_at",
        "updated_at",
        "has_accepted_communication",
    )
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "user__email",
        "user__username",
    )
    exclude = ("languages_spoken_at_home",)
    form = GuardianForm
    inlines = (RelationshipInline, LanguagesSpokenAtHomeInline)
    list_filter = (
        "has_accepted_communication",
        "children__project",
    )
    actions = (generate_children_event_history_markdown,)

    def user_link(self, guardian: Guardian):
        return mark_safe(
            '<a href="../user/%s">%s</a>' % (guardian.user_id, guardian.user)
        )


class PermissionFilterMixin:
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in ("permissions", "user_permissions"):
            qs = kwargs.get("queryset", db_field.remote_field.model.objects)
            qs = qs.filter(
                codename__in=Project.get_permission_codenames()
                + ReportPermission.get_codenames()
            )
            kwargs["queryset"] = qs

        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(get_user_model())
class UserAdmin(
    AuditlogAdminViewAccessLogMixin,
    PermissionFilterMixin,
    GuardedModelAdmin,
    DjangoUserAdmin,
):
    enable_list_view_audit_logging = True
    list_display = (
        "username",
        "id",
        "uuid",
        "guardian_link",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "date_joined",
        "last_login",
    )
    fieldsets = list(DjangoUserAdmin.fieldsets) + [
        ("UUID", {"fields": ("uuid",)}),
    ]
    readonly_fields = ("uuid",)
    list_filter = (
        ("guardian", admin.EmptyFieldListFilter),
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        "date_joined",
        "last_login",
    )
    search_fields = list(DjangoUserAdmin.search_fields) + [
        "uuid",
    ]
    date_hierarchy = "date_joined"

    def guardian_link(self, user):
        return mark_safe(
            '<a href="../guardian/%s">%s</a>' % (user.guardian.id, user.guardian)
        )


admin.site.unregister(Group)


class UserInline(admin.StackedInline):
    model = get_user_model().groups.through
    extra = 0
    autocomplete_fields = ("user",)


@admin.register(Group)
class GroupAdmin(
    AuditlogAdminViewAccessLogMixin, PermissionFilterMixin, DjangoGroupAdmin
):
    enable_list_view_audit_logging = False  # not needed in list view
    list_display = ("name", "get_user_count")
    inlines = (UserInline,)

    def get_user_count(self, obj):
        return obj.user_set.count()

    get_user_count.short_description = _("User count")
