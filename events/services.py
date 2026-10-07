from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from events.models import EventGroup
from kukkuu.consts import DATA_VALIDATION_ERROR


def validate_event_and_event_group_project_match(event):
    """
    Validate that an event belongs to the same project as its event group.

    This validation ensures that if an Event is assigned to an EventGroup,
    both share the exact same project_id. Uses the in-memory event_group
    instance if loaded to correctly honor unsaved project changes.
    """
    if event.event_group_id and event.project_id:
        try:
            # Use the instance directly to respect any unsaved in-memory changes
            event_group = event.event_group
        except EventGroup.DoesNotExist:
            return

        if event_group.project_id != event.project_id:
            raise ValidationError(
                _("The event and the event group must belong to the same project."),
                code=DATA_VALIDATION_ERROR,
            )


def validate_event_group_and_events_project_match(event_group):
    """
    Validate that an event group belongs to the same project as all its events.

    This prevents updating an EventGroup's project if it contains existing
    events that would be left orphaned in a different project. Evaluates
    prefetched events in-memory if available, or falls back to a database query.
    """
    if event_group.pk:
        # Check if any associated events belong to a different project
        # In-memory evaluation is possible if events were prefetched
        if getattr(event_group, "_prefetched_objects_cache", {}).get("events"):
            has_mismatch = any(
                event.project_id != event_group.project_id
                for event in event_group.events.all()
            )
        else:
            has_mismatch = event_group.events.exclude(
                project_id=event_group.project_id
            ).exists()

        if has_mismatch:
            raise ValidationError(
                _("The event group and its events must belong to the same project."),
                code=DATA_VALIDATION_ERROR,
            )
