import logging

from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from django_ilmoitin.admin import NotificationTemplateAdmin
from django_ilmoitin.models import NotificationTemplate

from .notification_importer import NotificationImporter, NotificationImporterException

logger = logging.getLogger(__name__)


class NotificationTemplateAdminWithImporter(NotificationTemplateAdmin):
    list_display = ("type", "get_sync_status")
    actions = ("update_selected",)
    ordering = ("type",)
    change_list_template = "notification_change_list.html"
    importer = None

    def changelist_view(self, request, *args, **kwargs):
        try:
            self.importer = NotificationImporter()
        except NotificationImporterException as e:
            self._send_error_message(request, e)
        return super().changelist_view(request, *args, **kwargs)

    @admin.display(
        description=_("in sync with the spreadsheet"),
        boolean=True,
    )
    def get_sync_status(self, obj):
        return self.importer.is_notification_in_sync(obj) if self.importer else None

    @admin.action(description=_("Update selected notifications from the spreadsheet"))
    def update_selected(self, request, queryset):
        if not self.importer:
            return

        try:
            num_of_updated = self.importer.update_notifications(queryset)
        except NotificationImporterException as e:
            self._send_error_message(request, e)
            return

        if num_of_updated:
            message = ngettext_lazy(
                f"Updated {num_of_updated} notification.",
                f"Updated {num_of_updated} notifications.",
                num_of_updated,
            )
        else:
            message = _("The selected notifications were in sync already.")
        self.message_user(request, message, messages.SUCCESS)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-missing-notifications/",
                self.admin_site.admin_view(self.import_missing_notifications),
                name="import-missing-notifications",
            ),
        ]
        return custom_urls + urls

    def import_missing_notifications(self, request):
        if self.importer:
            try:
                num_of_created = self.importer.create_missing_notifications()
            except NotificationImporterException as e:
                self._send_error_message(request, e)
            else:
                if num_of_created:
                    message = ngettext_lazy(
                        f"Imported {num_of_created} new notification.",
                        f"Imported {num_of_created} new notifications.",
                        num_of_created,
                    )
                else:
                    message = _("No missing notifications.")
                self.message_user(request, message, messages.SUCCESS)

        return HttpResponseRedirect(
            reverse("admin:django_ilmoitin_notificationtemplate_changelist")
        )

    def _send_error_message(self, request, message):
        logger.error(message)
        self.message_user(request, message, messages.ERROR)


if settings.KUKKUU_NOTIFICATIONS_SHEET_ID:
    admin.site.unregister(NotificationTemplate)
    admin.site.register(NotificationTemplate, NotificationTemplateAdminWithImporter)
