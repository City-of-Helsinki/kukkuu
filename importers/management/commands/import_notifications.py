from django.core.management import BaseCommand

from importers.notification_importer import (
    NotificationImporter,
    NotificationImporterException,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Importing notifications from Google Sheets...")

        try:
            importer = NotificationImporter()
            (
                num_of_created,
                num_of_updated,
            ) = importer.create_missing_and_update_existing_notifications()
        except NotificationImporterException as e:
            self.stdout.write(self.style.ERROR(e))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Great success! Created {num_of_created} new notification(s) and "
                f"updated {num_of_updated} already existing notification(s)."
            )
        )
