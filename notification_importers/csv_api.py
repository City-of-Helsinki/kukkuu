import csv
import logging

from django.http import HttpResponse
from django_ilmoitin.models import NotificationTemplate
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser

from kukkuu.oidc import BrowserTestAwareJWTAuthentication

logger = logging.getLogger(__name__)


class ExportCsvMixin:
    """
    Mixin to provide CSV export functionality.
    This mixin can be used in views to export data as a CSV file.
    """

    def get_attributes(self) -> list[str]:
        """
        Returns the attributes to be exported in the CSV file.
        This can be overridden in subclasses to customize the attributes.
        """
        return self.attributes

    def get_languages(self) -> list[str]:
        """
        Returns the languages to be used for translated fields in the CSV file.
        This can be overridden in subclasses to customize the languages.
        """
        return self.languages

    def create_csv_response_writer(self, filename):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(filename)

        """
        Adding BOM is not advicable, and UTF-8 shouldn't even have that,
        but Microsoft product seems to sometimes need it.
        """
        response.write("\ufeff")

        """
        CSV is a delimited text file that uses a comma to separate values
        (many implementations of CSV import/export tools allow other
        separators to be used; for example, the use of a "Sep=^" row
        as the first row in the csv file will cause Excel to open
        the file expecting caret "^" to be the separator instead of comma ",").
        ~ https://en.wikipedia.org/wiki/Comma-separated_values.
        NOTE: At least when using a comma as a delimiter,
        the separator is needed to be defined for Microsoft Excel.
        NOTE: When tested with Microsoft Excel for Mac, strangely,
        it seems to help Excel to choose the delimiter, but seems to break encoding
        and the scandinavian letters are not shown properly.
        """
        # response.write(f"sep={self.csv_delimiter}{self.csv_dialect.lineterminator}")

        """
        The CSV library uses Excel as the default dialect,
        but Excel still seems not to work properly with it,
        since there were issues with the separator and the encoding.
        Using the semicolon (";") as a delimiter
        seems to fix UTF-8 issues with Microsoft Excel.
        """
        writer = csv.writer(
            response, dialect=self.csv_dialect, delimiter=self.csv_delimiter
        )

        return writer, response

    def write_csv_header_row(self, writer: csv.writer) -> None:
        """
        Writes the header row for the CSV file.
        This row contains the column names for the notification templates.

        @example:
        header_row = [
            "Notification Type",
            "Subject | FI",
            "Subject | SV",
            "Subject | EN",
            "Body Text | FI",
            "Body Text | SV",
            "Body Text | EN"
        ]
        """
        logger.debug("Writing header row for CSV file")
        header_row = []
        for attr in self.get_attributes():
            verbose_field_name = self._get_verbose_field_name(attr).capitalize()

            if not self._is_translated_field(attr):
                header_row.append(verbose_field_name)
            else:
                for lang in self.get_languages():
                    header_row.append(f"{verbose_field_name} | {lang.upper()}")
        # Write the header row to the CSV file
        writer.writerow(header_row)

    def write_csv_data_row(
        self, writer: csv.writer, template: NotificationTemplate
    ) -> None:
        """
        Writes a single row of data for a notification template to the CSV file.
        """
        logger.debug(f"Writing data row for template: {template.type}")
        data_row = []
        for attr in self.get_attributes():
            if not self._is_translated_field(attr):
                data_row.append(getattr(template, attr))
            else:
                for lang in self.get_languages():
                    data_row.append(
                        template.safe_translation_getter(
                            attr, language_code=lang, default=""
                        )
                    )
        writer.writerow(data_row)

    def _is_translated_field(self, field_name: str) -> bool:
        """
        Checks if the given field name is a translated field in the model.
        Returns True if it is a translated field, otherwise False.
        """
        return field_name in self.model._parler_meta.get_translated_fields()

    def _get_verbose_field_name(self, field_name: str) -> str:
        """
        Returns the verbose name of a field from the model's metadata.
        If the field does not exist, it returns the field name itself.
        """
        logger.debug(f"Getting verbose name for field: {field_name}")
        try:
            if self._is_translated_field(field_name):
                # If the field is a translated field, get the verbose name
                # from the parler model
                parler_model = self.model._parler_meta.get_model_by_field(field_name)
                field = parler_model._meta.get_field(field_name)
            else:
                # If the field is a regular field, get the verbose name from the model
                field = self.model._meta.get_field(field_name)
            if hasattr(field, "verbose_name"):
                if field.verbose_name:
                    return field.verbose_name
            return field.name

        except Exception as e:
            logger.error(f"Error getting verbose name for field '{field_name}': {e}")
            return field_name


class ExportNotificationTemplatesCsvView(ExportCsvMixin, GenericAPIView):
    """
    View to export notification templates as a CSV file.
    """

    model = NotificationTemplate
    queryset = NotificationTemplate.objects.all()
    serializer_class = None
    authentication_classes = [BrowserTestAwareJWTAuthentication, SessionAuthentication]
    permission_classes = [IsAdminUser]
    csv_dialect = csv.excel
    csv_delimiter = ";"

    attributes = [
        "type",
        "subject",
        "body_text",
        "body_html",
    ]
    languages = ["fi", "sv", "en"]
    csv_filename = "kukkuu_notification_templates"

    def get_queryset(self):
        return self.queryset.order_by("type")

    def get(self, request, *args, **kwargs):
        return self._write_csv_response()

    def _write_csv_response(self) -> HttpResponse:
        """
        Writes the CSV response for the notification templates.
        This method creates a CSV response with the notification templates data.
        It uses the `create_csv_response_writer` method to create a CSV writer
        and writes the header row and data rows using `write_csv_header_row` and
        `write_csv_data_row` methods respectively.
        """
        logger.debug("Creating CSV response for notification templates")
        writer, response = self.create_csv_response_writer(filename=self.csv_filename)
        self.write_csv_header_row(writer)
        for template in self.get_queryset():
            self.write_csv_data_row(writer, template)
        return response
