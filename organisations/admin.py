from django.contrib import admin
from django.contrib.auth import get_user_model

from organisations.models import Organisation


class OrganisationUserInline(admin.TabularInline):
    model = get_user_model().organisations.through
    extra = 0
    autocomplete_fields = ("user",)
    verbose_name = "User"
    verbose_name_plural = "Users"


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_system", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_system", "created_at")
    readonly_fields = ("is_system",)
    date_hierarchy = "created_at"
    inlines = [OrganisationUserInline]

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)
