from django.contrib import admin

from .models import VerificationToken


def verification_token_user_full_name(obj):
    if obj.user is not None:
        return obj.user.guardian.full_name
    return obj.user.username


verification_token_user_full_name.short_description = "Name"


@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "verification_type",
        "content_type",
        "object_id",
        verification_token_user_full_name,
        "email",
        "created_at",
        "expiry_date",
        "is_active",
    )
    list_display_links = ("key",)
    list_filter = ("created_at", "is_active", "verification_type", "content_type")
    autocomplete_fields = ("user",)
    date_hierarchy = "created_at"
    search_fields = (
        "key__exact",
        "content_type__model__exact",
        "object_id__exact",
        "user__guardian__first_name__exact",
        "user__guardian__last_name__exact",
        "user__username",
        "user__email__exact",
        "email__exact",
    )
    ordering = (
        "created_at",
        "expiry_date",
    )
