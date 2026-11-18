import sys

from django.core.management import BaseCommand
from django.db.models import Count

from events.models import Event


class Command(BaseCommand):
    help = (
        "Check external ticket system events before migrating them to a "
        "single occurrence. Validates that all external events have "
        "ticket_system_end_time populated and no external event has more "
        "than one occurrence. Use --fix to automatically populate missing "
        "ticket_system_end_time from published_at (or created_at if "
        "published_at is empty)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help=(
                "Automatically populate missing ticket_system_end_time using "
                "published_at (or created_at if published_at is empty)."
            ),
        )

    def _fix_missing_end_times(self, events_without_end_time):
        fixed_count = 0
        for event in events_without_end_time:
            fallback_time = event.published_at or event.created_at
            source = "published_at" if event.published_at else "created_at"
            event.ticket_system_end_time = fallback_time
            event.save(update_fields=["ticket_system_end_time"])
            self.stdout.write(
                f"Fixed event id={event.id} ({event.name or 'unnamed'}): "
                f"set ticket_system_end_time to {fallback_time} (from {source})."
            )
            fixed_count += 1
        self.stdout.write(
            self.style.SUCCESS(f"Successfully fixed {fixed_count} external event(s).")
        )

    def _report_missing_end_times(self, events_without_end_time, *, fix: bool) -> bool:
        if not events_without_end_time.exists():
            return False

        self.stderr.write(
            self.style.ERROR(
                f"\nFound {events_without_end_time.count()} external event(s) "
                "with missing ticket_system_end_time:"
            )
        )
        for event in events_without_end_time:
            self.stderr.write(
                f"  - id={event.id}, name='{event.name}', project={event.project}, "
                f"created_at={event.created_at}, published_at={event.published_at}"
            )
        if not fix:
            self.stderr.write(
                self.style.WARNING(
                    "\nHint: Run this command with --fix to automatically "
                    "populate missing ticket_system_end_time from published_at "
                    "(or created_at if published_at is empty)."
                )
            )
        return True

    def _report_multiple_occurrences(self, events_with_multiple_occurrences) -> bool:
        if not events_with_multiple_occurrences.exists():
            return False

        self.stderr.write(
            self.style.ERROR(
                f"\nFound {events_with_multiple_occurrences.count()} external event(s) "
                "with more than 1 occurrence:"
            )
        )
        for event in events_with_multiple_occurrences:
            self.stderr.write(
                f"  - id={event.id}, name='{event.name}', "
                f"occurrences_count={event.occ_count}"
            )
        return True

    def handle(self, *args, **options):
        fix = options["fix"]
        external_events = Event.objects.exclude(ticket_system=Event.INTERNAL)
        total_count = external_events.count()

        self.stdout.write(
            f"Found {total_count} external ticket system event(s) in total."
        )

        missing_end_time = external_events.filter(ticket_system_end_time__isnull=True)
        multiple_occurrences = external_events.annotate(
            occ_count=Count("occurrences")
        ).filter(occ_count__gt=1)

        if fix and missing_end_time.exists():
            self._fix_missing_end_times(missing_end_time)
            missing_end_time = external_events.filter(
                ticket_system_end_time__isnull=True
            )

        has_missing = self._report_missing_end_times(missing_end_time, fix=fix)
        has_multiple = self._report_multiple_occurrences(multiple_occurrences)

        if has_missing or has_multiple:
            sys.exit(1)

        self.stdout.write(
            self.style.SUCCESS(
                f"All {total_count} external ticket system event(s) are valid for "
                "occurrence migration."
            )
        )
