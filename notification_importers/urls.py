from django.urls import path

from notification_importers.csv_api import ExportNotificationTemplatesCsvView

urlpatterns = [
    path(
        "csv_api/export-notification-templates/",
        ExportNotificationTemplatesCsvView.as_view(),
        name="export-notification-templates-csv",
    ),
]
