from django.core.management import BaseCommand

from events.models import Enrolment


class Command(BaseCommand):
    help = "Sends notifications about approaching occurrences to enrolled children."

    def handle(self, *args, **options):
        self.stdout.write("Sending reminder notifications...")

        count = Enrolment.objects.send_reminder_notifications()

        self.stdout.write(f"Sent {count} occurrence reminder notification(s).")
