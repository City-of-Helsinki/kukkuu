import csv
import io
from collections import defaultdict
from logging import getLogger
from typing import DefaultDict, Dict, Mapping, Optional, Sequence, Tuple

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django_ilmoitin.dummy_context import dummy_context
from django_ilmoitin.models import NotificationTemplate, NotificationTemplateException
from django_ilmoitin.utils import render_notification_template
from parler.utils.context import switch_language
from requests import RequestException

# {
#     "<notification type>": {
#         "<language code>": {
#             "<field name>": "<field value>",
#             ...
#         },
#         ...
#     },
#     ...
# }
SheetData = Mapping[str, Mapping[str, Mapping[str, str]]]


logger = getLogger(__name__)


class NotificationImporterException(Exception):  # noqa: N818
    pass


class NotificationImporter:
    """Imports NotificationTemplates from Google Sheets."""

    TIMEOUT = 5
    LANGUAGES = settings.PARLER_SUPPORTED_LANGUAGE_CODES
    FIELDS = ("subject", "body_text", "body_html")
    HEADER_FIELD_AND_LANGUAGE_SEPARATOR = "|"

    def __init__(self, sheet_id: str = None) -> None:
        self.sheet_id = sheet_id or settings.KUKKUU_NOTIFICATIONS_SHEET_ID
        if not self.sheet_id:
            raise NotificationImporterException("Sheet ID not set.")

        self.sheet_data: SheetData = self._fetch_data()

    @transaction.atomic()
    def create_missing_and_update_existing_notifications(self) -> Tuple[int, int]:
        num_of_created = self.create_missing_notifications()
        num_of_updated = self.update_notifications(NotificationTemplate.objects.all())
        return num_of_created, num_of_updated

    @transaction.atomic()
    def create_missing_notifications(self) -> int:
        new_types = set(self.sheet_data.keys()) - set(
            NotificationTemplate.objects.values_list("type", flat=True)
        )
        for new_type in new_types:
            new_notification = NotificationTemplate(type=new_type)
            self._create_or_update_notification_using_sheet_data(new_notification)

        return len(new_types)

    @transaction.atomic()
    def update_notifications(
        self, notifications: Sequence[NotificationTemplate]
    ) -> int:
        num_of_updated = 0

        for notification in notifications:
            if self.is_notification_in_sync(notification) is False:
                self._create_or_update_notification_using_sheet_data(notification)
                num_of_updated += 1

        return num_of_updated

    def is_notification_in_sync(
        self, notification: NotificationTemplate
    ) -> Optional[bool]:
        if notification.type not in self.sheet_data:
            return None

        for language in self.LANGUAGES:
            try:
                translation_obj = notification.translations.get(language_code=language)
            except ObjectDoesNotExist:
                translation_obj = None

            for field in self.FIELDS:
                current_value = (
                    self.clean_text(getattr(translation_obj, field))
                    if translation_obj
                    else ""
                )
                sheet_value = self._get_value_from_sheet(
                    notification.type, field, language
                )

                if current_value != sheet_value:
                    return False

        return True

    @property
    def url(self) -> str:
        return (
            f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/export?format=csv"
        )

    def _fetch_data(self) -> SheetData:
        csv_data = self._fetch_csv_data()
        return self._get_sheet_data_from_csv_file(io.StringIO(csv_data))

    def _fetch_csv_data(self) -> str:
        try:
            response = requests.get(self.url, timeout=self.TIMEOUT)
            response.raise_for_status()
        except RequestException as e:
            raise NotificationImporterException(
                f"Error fetching data from the spreadsheet: {e}"
            ) from e
        return response.content.decode("utf-8")

    def _get_sheet_data_from_csv_file(self, csv_file: io.StringIO) -> SheetData:
        reader = csv.DictReader(csv_file)
        sheet_data = {}

        for row in reader:
            notification_data: DefaultDict[str, Dict[str, str]] = defaultdict(dict)

            row_items = iter(row.items())
            # the first column contains notification type
            notification_type = next(row_items)[1].lower()

            for header, content in row_items:
                field, language = self._get_field_and_language_from_header(header)
                notification_data[language][field] = self.clean_text(content)

            sheet_data[notification_type] = notification_data

        return sheet_data

    def _create_or_update_notification_using_sheet_data(
        self, notification: NotificationTemplate
    ):
        creating = not bool(notification.pk)

        for language in self.LANGUAGES:
            with switch_language(notification, language):
                for field in self.FIELDS:
                    setattr(
                        notification,
                        field,
                        self._get_value_from_sheet(notification.type, field, language),
                    )
                notification.save()

            # Test that the notification can be rendered without errors.
            # This create/update method is called inside a transaction so the
            # notification will not get actually saved in case of an error.
            try:
                render_notification_template(
                    notification,
                    context=dummy_context.get(notification.type),
                    language_code=language,
                )
            except NotificationTemplateException as e:
                raise NotificationImporterException(
                    f'Error rendering notification "{notification}": {e}'
                ) from e

        logger.info(
            f'{"Created" if creating else "Updated"} notification "{notification}"'
        )

    def _get_field_and_language_from_header(self, header: str) -> Tuple[str, str]:
        field, language = header.split(self.HEADER_FIELD_AND_LANGUAGE_SEPARATOR)
        return field.lower().strip(), language.lower().strip()

    def _get_value_from_sheet(
        self, notification_type: str, field: str, language: str
    ) -> str:
        return (
            self.sheet_data.get(notification_type, {}).get(language, {}).get(field, "")
        )

    @staticmethod
    def clean_text(text: str) -> str:
        return text.replace("\u202f", " ").replace("\r\n", "\n")
