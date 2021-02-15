from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from guardian.admin import (
    AdminGroupObjectPermissionsForm,
    AdminUserObjectPermissionsForm,
    GuardedModelAdmin,
)
from parler.admin import TranslatableAdmin
from projects.models import Project


class PermissionFilterMixin:
    def get_obj_perms_field_choices(self):
        choices = super().get_obj_perms_field_choices()
        return [c for c in choices if c[0] in Project.get_permission_codenames()]


class UserPermissionsForm(PermissionFilterMixin, AdminUserObjectPermissionsForm):
    pass


class GroupPermissionsForm(PermissionFilterMixin, AdminGroupObjectPermissionsForm):
    pass


class UserSelectForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.possible_admins(), required=True
    )


class GroupSelectForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True)


@admin.register(Project)
class ProjectAdmin(TranslatableAdmin, GuardedModelAdmin):
    change_form_template = "project_change_form.html"
    list_display = ("year", "name", "single_events_allowed")
    fields = ("year", "name", "single_events_allowed")

    def get_obj_perms_base_context(self, request, obj):
        context = super().get_obj_perms_base_context(request, obj)
        if "model_perms" in context:
            context["model_perms"] = context["model_perms"].filter(
                codename__in=Project.get_permission_codenames()
            )
        return context

    def get_obj_perms_manage_user_form(self, request):
        return UserPermissionsForm

    def get_obj_perms_manage_group_form(self, request):
        return GroupPermissionsForm

    def get_obj_perms_user_select_form(self, request):
        return UserSelectForm

    def get_obj_perms_group_select_form(self, request):
        return GroupSelectForm
