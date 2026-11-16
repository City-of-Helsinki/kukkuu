"""
Populate a single occurrence with the global system venue for existing external ticket system events.
"""

import logging

from django.conf import settings
from django.db import migrations
from django.db.models import Q

logger = logging.getLogger(__name__)


def populate_external_event_occurrences(apps, schema_editor):
    """
    Ensure every external ticket system event has exactly one occurrence using the global system venue.
    """
    Event = apps.get_model("events", "Event")
    Occurrence = apps.get_model("events", "Occurrence")
    Venue = apps.get_model("venues", "Venue")
    VenueTranslation = apps.get_model("venues", "VenueTranslation")
    EventTranslation = apps.get_model("events", "EventTranslation")

    external_events = Event.objects.exclude(ticket_system="internal")
    if not external_events.exists():
        return

    null_end_time_count = external_events.filter(
        ticket_system_end_time__isnull=True
    ).count()
    if null_end_time_count > 0:
        raise RuntimeError(
            f"Cannot migrate external events to single occurrence: found "
            f"{null_end_time_count} external event(s) with NULL ticket_system_end_time. "
            "Run 'python manage.py check_external_events_before_occurrence_migration "
            "--fix' to populate them before running this migration."
        )

    system_venue_name = settings.KUKKUU_DEFAULT_VENUE_NAME
    system_venue = Venue.objects.filter(is_system=True).first()
    if not system_venue:
        system_venue = Venue.objects.create(is_system=True, project=None)
        for lang_code in settings.PARLER_SUPPORTED_LANGUAGE_CODES:
            VenueTranslation.objects.create(
                master=system_venue,
                language_code=lang_code,
                name=system_venue_name,
            )
        logger.info(
            "Created system venue %s with name '%s'",
            system_venue.pk,
            system_venue_name,
        )

    default_lang = settings.LANGUAGE_CODE

    for event in external_events:
        first_occurrence = Occurrence.objects.filter(event=event).first()
        if first_occurrence:
            first_occurrence.time = event.ticket_system_end_time
            first_occurrence.ticket_system_url = event.ticket_system_url
            first_occurrence.venue = system_venue
            first_occurrence.save(update_fields=["time", "ticket_system_url", "venue"])
            logger.info(
                "Updated occurrence %s for external event %s",
                first_occurrence.pk,
                event.pk,
            )
        else:
            translated_langs = list(
                EventTranslation.objects.filter(master=event).values_list(
                    "language_code", flat=True
                )
            )
            if default_lang in translated_langs:
                lang = default_lang
            elif translated_langs:
                lang = translated_langs[0]
            else:
                lang = default_lang

            occ = Occurrence.objects.create(
                event=event,
                time=event.ticket_system_end_time,
                ticket_system_url=event.ticket_system_url,
                venue=system_venue,
                occurrence_language=lang,
            )
            logger.info("Created occurrence %s for external event %s", occ.pk, event.pk)


def revert_external_event_occurrences(apps, schema_editor):
    """
    Remove occurrences created for external ticket system events that use the system venue.
    """
    Occurrence = apps.get_model("events", "Occurrence")
    qs = Occurrence.objects.filter(
        ~Q(event__ticket_system="internal"),
        event__ticket_system__isnull=False,
        venue__is_system=True,
    )
    count = qs.count()
    qs.delete()
    logger.info("Deleted %d external event occurrence(s)", count)


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0037_occurrence_accessibilities"),
        ("venues", "0008_venue_is_system"),
    ]

    operations = [
        migrations.RunPython(
            populate_external_event_occurrences,
            revert_external_event_occurrences,
        ),
    ]
