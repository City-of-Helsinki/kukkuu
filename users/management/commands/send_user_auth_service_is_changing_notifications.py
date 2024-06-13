from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime

from users.services import AuthServiceNotificationService


class Command(BaseCommand):
    help = "Sends user authorization service is changing notifications."

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--date_of_change",
            type=str,
            help="Date of the change of the auth service as a formatted str "
            "(e.g., '17.6.2024'). "
            "The default should be given in the notification template.",
            default=None,  # The default should be given in the notification template.
        )
        parser.add_argument(
            "-j",
            "--joined_before",
            type=str,
            help="Users who have joined before this datetime are included in queryset "
            "Datetime in ISO format (e.g., '2024-06-17T15:00:00Z').",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--emails",
            nargs="+",  # Accept multiple values as a list
            help="List of guardian emails to send notifications to (space-separated).",
        )
        parser.add_argument(
            "--include_non_obsoleted",
            action="store_true",
            help="Should the non obsoleted accounts be included in the recipients? "
            "By default only the obsoleted accounts are included in the query set.",
            default=False,
        )
        parser.add_argument(
            "-m",
            "--max_guardian_count",
            type=int,
            help="Maximum number of guardians to send notifications to. "
            "By default there's no limit.",
            default=None,
        )

    def _get_joined_before(self, **options):
        joined_before_datetime_str = options["joined_before"]
        invalid_date_error_str = (
            "Invalid datetime format with joined_before. "
            "Use ISO format (YYYY-MM-DDTHH:MM:SS)."
        )
        if joined_before_datetime_str:
            try:
                joined_before_datetime = parse_datetime(joined_before_datetime_str)
                if joined_before_datetime is None:
                    raise CommandError(invalid_date_error_str)
                return joined_before_datetime
            except ValueError:
                raise CommandError(invalid_date_error_str)
        return None

    def handle(self, *args, **options):
        date_of_change_str = options["date_of_change"]
        user_joined_before = self._get_joined_before(**options)
        guardian_emails = options.get("emails", None)
        obsoleted_users_only = not options["include_non_obsoleted"]
        max_guardian_count = options["max_guardian_count"]
        Guardian = apps.get_model("users", "Guardian")

        self.stdout.write("Sending user auth service is changing notifications...")

        guardians = Guardian.objects.for_auth_service_is_changing_notification(
            user_joined_before=user_joined_before,
            obsoleted_users_only=obsoleted_users_only,
            guardian_emails=guardian_emails,
        )[:max_guardian_count]
        count = guardians.count()

        AuthServiceNotificationService.send_user_auth_service_is_changing_notifications(
            guardians=guardians, date_of_change_str=date_of_change_str
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Sent {count} user auth service is changing notifications."
            )
        )
