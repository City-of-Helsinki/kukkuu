from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime

from users.services import AuthServiceNotificationService


class Command(BaseCommand):
    help = "Sends user authorization service is changing notifications."

    def add_arguments(self, parser):
        # user_joined_before: Optional[datetime] = None, obsoleted_users_only=True
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
            help="Users who has joined before this datetime are included in queryset "
            "Datetime in ISO format (e.g., '2024-06-17T15:00:00Z')",
            default=None,
        )
        parser.add_argument(
            "--include_non_obsoleted",
            action="store_true",
            help="Date of the change in auth server. "
            "The default should be given in the notification template.",
            default=False,
        )

    def _get_joined_before(self, **options):
        joined_before_datetime_str = options["joined_before"]
        invalid_date_error_str = "Invalid datetime format with joined_before. Use ISO format (YYYY-MM-DDTHH:MM:SS)."  # noqa
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
        obsoleted_users_only = not options["include_non_obsoleted"]
        Guardian = apps.get_model("users", "Guardian")

        self.stdout.write("Sending user auth service is changing notifications...")

        guardians = Guardian.objects.for_auth_service_is_changing_notification(
            user_joined_before=user_joined_before,
            obsoleted_users_only=obsoleted_users_only,
        )
        count = guardians.count()

        AuthServiceNotificationService.send_user_auth_service_is_changing_notifications(
            guardians=guardians, date_of_change_str=date_of_change_str
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Sent {count} user auth service is changing notifications."
            )
        )
