from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from messaging.exceptions import AlreadySentError

from .models import Message


@admin.register(Message)
class MessageAdmin(TranslatableAdmin):
    list_display = (
        "subject",
        "project",
        "protocol",
        "sent_at",
        "get_recipient_count",
        "created_at",
        "updated_at",
        "get_occurrences_names",
    )
    fields = (
        "project",
        "protocol",
        "subject",
        "body_text",
        "recipient_selection",
        "event",
        "occurrences",
        "created_at",
        "updated_at",
        "get_recipient_count",
    )
    list_filter = ("protocol", "sent_at", "created_at", "updated_at")
    readonly_fields = ("get_recipient_count", "created_at", "updated_at")
    search_fields = (
        "translations__subject",
        "translations__body_text",
    )
    date_hierarchy = "created_at"
    actions = ("send",)

    def get_occurrences_names(self, obj):
        return ", ".join(
            [
                f"{occurrence.event}: {occurrence}"
                for occurrence in obj.occurrences.all()
            ]
        )

    get_occurrences_names.short_description = _("occurrences")

    def get_recipient_count(self, obj):
        return str(obj.get_recipient_count()) + (
            str(_(" (if sent now)")) if not obj.sent_at else ""
        )

    get_recipient_count.short_description = _("recipient count")

    def send(self, request, queryset):
        sent_count = 0
        for obj in queryset:
            try:
                obj.send()
                sent_count += 1
            except AlreadySentError:
                pass
        self.message_user(request, _("%s successfully sent.") % sent_count)
