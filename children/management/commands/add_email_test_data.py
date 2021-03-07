from datetime import date

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db import transaction
from mailer.models import Message
from projects.factories import ProjectFactory
from projects.models import Project

from children.factories import ChildWithGuardianFactory
from events.factories import EventFactory
from events.models import Event
from users.factories import GuardianFactory
from users.models import Guardian

NUM_OF_CHILDREN = 10
PROJECT_YEAR = 1917
TEST_EVENT_DURATION = 12345


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("children", nargs="?", type=int)

        parser.add_argument(
            "--flush", action="store_true",
        )

        parser.add_argument(
            "--publish", action="store_true",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        import random

        identifier = random.randint(1, 100000)
        self.stdout.write(f"Adding email test data...")

        try:
            project = Project.objects.get(year=PROJECT_YEAR)
        except Project.DoesNotExist:
            project = ProjectFactory(
                name=f"test project {PROJECT_YEAR}", year=PROJECT_YEAR
            )

        if options["flush"]:
            self.stdout.write("Flushing...")
            guardians = Guardian.objects.filter(children__in=project.children.all())
            get_user_model().objects.filter(guardian__in=guardians).delete()
            guardians.delete()
            project.children.delete()
            Event.objects.filter(project=project, duration=TEST_EVENT_DURATION).delete()
            Message.objects.all().delete()

        try:
            event = Event.objects.get(project=project, duration=TEST_EVENT_DURATION)
        except Event.DoesNotExist:
            event = EventFactory(
                project=project, name="Email test event", duration=TEST_EVENT_DURATION
            )
            event.description += f"\n\nIdentifier: {identifier}."
            self.stdout.write(f"Created test event {event}")

        num_of_children = options["children"]
        if num_of_children:
            self.stdout.write(f"Adding {num_of_children} children...")

            for i in range(num_of_children):
                guardian = GuardianFactory(
                    user__first_name="Email Test User",
                    user__username=f"kukkuu-test-{i}",
                    user__email=f"kukkuu-test-{i % 4}@mailinator.com",
                )
                child = ChildWithGuardianFactory(
                    relationship__guardian=guardian,
                    project=project,
                    birthdate=date(PROJECT_YEAR, 1, 1),
                )

                self.stdout.write(
                    f"Created {child} with guardian email {guardian.email}"
                )

        if options["publish"]:
            event.publish()
            self.stdout.write(
                f"Published the test event, {Message.objects.count()} messages "
                f"waiting to be sent. Identifier: {identifier}."
            )

        self.stdout.write("Done!")
