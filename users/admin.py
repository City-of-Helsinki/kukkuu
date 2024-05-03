from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from guardian.admin import GuardedModelAdmin

from children.models import Relationship
from languages.models import Language
from projects.models import Project
from reports.models import Permission as ReportPermission
from users.models import Guardian


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


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "language",
        "created_at",
        "updated_at",
        "has_accepted_marketing",
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
    list_filter = ("children__project", "has_accepted_marketing")


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


@admin.action(description="Mark selected users as obsoleted")
def make_obsoleted(modeladmin, request, queryset):
    queryset.update(is_obsolete=True)


@admin.register(get_user_model())
class UserAdmin(PermissionFilterMixin, GuardedModelAdmin, DjangoUserAdmin):
    list_display = (
        "username",
        "id",
        "uuid",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_obsolete",
        "date_joined",
        "last_login",
    )
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("UUID", {"fields": ("uuid",)}),
        ("Auth", {"fields": ("is_obsolete",)}),
    )
    readonly_fields = ("uuid",)
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "is_obsolete",
        "groups",
        "date_joined",
        "last_login",
    )
    search_fields = DjangoUserAdmin.search_fields + ("uuid",)
    date_hierarchy = "date_joined"
    actions = [make_obsoleted]


admin.site.unregister(Group)


class UserInline(admin.StackedInline):
    model = get_user_model().groups.through
    extra = 0


@admin.register(Group)
class GroupAdmin(PermissionFilterMixin, DjangoGroupAdmin):
    list_display = ("name", "get_user_count")
    inlines = (UserInline,)

    def get_user_count(self, obj):
        return obj.user_set.count()

    get_user_count.short_description = _("User count")
