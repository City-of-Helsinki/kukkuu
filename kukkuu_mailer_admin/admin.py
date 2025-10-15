from auditlog_extra.mixins import AuditlogAdminViewAccessLogMixin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from mailer.admin import MessageAdmin, MessageLogAdmin, show_to
from mailer.models import RESULT_CODES, Message, MessageLog


def custom_titled_filter(title: str):
    """A decorator to change a Django list filter title."""

    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


@admin.display(description=_("Sent to mail server"))
def sent_to_mail_server(message: MessageLog) -> str:
    """Override the result column in `list_display`.
    A `list_display` column can be overridden by redefining
    a `short_description`

    @example
    sent_to_mail_server.short_description = "Sent to mail server"

    Args:
        message (MessageLog): related MessageLog instance

    Returns:
        str: text for the value of the result field.
    """
    return next(text for (code, text) in RESULT_CODES if code == message.result)


class KukkuuMessageLogAdmin(AuditlogAdminViewAccessLogMixin, MessageLogAdmin):
    """Override the MessageLogAdmin provided by django_mailer."""

    enable_list_view_audit_logging = True
    list_display = [
        "id",
        show_to,
        "subject",
        "message_id",
        "when_attempted",
        sent_to_mail_server,  # Result column label changed
    ]
    list_filter = [("result", custom_titled_filter(_("Sent to mail server")))]


# Unregister the MessageLog admin provided by the `django_mailer`.
admin.site.unregister(MessageLog)
# Register a new admin for the MessageLog.
admin.site.register(MessageLog, KukkuuMessageLogAdmin)


class KukkuuMessageAdmin(AuditlogAdminViewAccessLogMixin, MessageAdmin):
    """Override the MessageAdmin provided by django_mailer."""

    enable_list_view_audit_logging = True


# Unregister the Message admin provided by the `django_mailer`.
admin.site.unregister(Message)
# Register a new admin for the Message.
admin.site.register(Message, KukkuuMessageAdmin)
