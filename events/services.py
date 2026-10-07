import logging
import os
from copy import deepcopy

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _

from common.utils import get_obj_if_user_can_administer
from events.models import Event, EventGroup
from kukkuu.consts import DATA_VALIDATION_ERROR
from kukkuu.exceptions import DataValidationError, SingleEventsDisallowedError
from projects.models import Project

logger = logging.getLogger(__name__)

_DEFAULT_TICKET_SYSTEM_URL = "https://example.com"


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


def validate_event_group_and_events_project_match(
    event_group, *, events=None, project=None
):
    """
    Validate that an event group belongs to the same project as all its events.

    This prevents updating an EventGroup's project if it contains existing
    events that would be left orphaned in a different project. Evaluates
    explicitly provided events in-memory if given, prefetched events if
    available, or falls back to a database query.
    """
    project_id = (
        project.pk if project is not None else getattr(event_group, "project_id", None)
    )

    if events is not None:
        has_mismatch = any(event.project_id != project_id for event in events)
    elif event_group and event_group.pk:
        # Check if any associated events belong to a different project
        # In-memory evaluation is possible if events were prefetched
        if getattr(event_group, "_prefetched_objects_cache", {}).get("events"):
            has_mismatch = any(
                event.project_id != project_id for event in event_group.events.all()
            )
        else:
            has_mismatch = event_group.events.exclude(project_id=project_id).exists()
    else:
        has_mismatch = False

    if has_mismatch:
        raise ValidationError(
            _("The event group and its events must belong to the same project."),
            code=DATA_VALIDATION_ERROR,
        )


class EventAPIService:
    """
    Service class for Event and EventGroup GraphQL API business logic.
    """

    @staticmethod
    def _copy_image_file(source, target):
        """Copy the image file from source to target, if one exists."""
        if source.image:
            try:
                name = os.path.basename(source.image.name)
                target.image.save(name, ContentFile(source.image.read()), save=True)
            except Exception:
                logger.exception(
                    "Failed to copy image from %s to %s", source.pk, target.pk
                )

    @staticmethod
    def resolve_event_target(info, project_global_id, event_group_global_id):
        """
        Resolve the target Project and EventGroup for a new event.
        Ensures the user has administration rights and validates project matching
        and single-event permissions.
        """
        project = get_obj_if_user_can_administer(info, project_global_id, Project)
        event_group = None
        if event_group_global_id:
            event_group = get_obj_if_user_can_administer(
                info, event_group_global_id, EventGroup
            )
            if event_group.project_id != project.pk:
                raise DataValidationError("Event group does not belong to the project.")
        elif not project.single_events_allowed:
            raise SingleEventsDisallowedError(
                f"Single events are disallowed in project {project}."
            )
        return project, event_group

    @classmethod
    def _seed_translations(cls, kwargs, source):
        """
        Seed omitted translations from source object before applying submitted
        translations.
        """
        source_translations = {
            tr.language_code: {
                "language_code": tr.language_code,
                "name": tr.name,
                "short_description": tr.short_description,
                "description": tr.description,
                "image_alt_text": tr.image_alt_text,
            }
            for tr in source.translations.all()
        }
        if "translations" not in kwargs or kwargs["translations"] is None:
            kwargs["translations"] = list(source_translations.values())
        else:
            submitted = kwargs.pop("translations") or []
            for tr_input in submitted:
                lang = tr_input["language_code"]
                if lang in source_translations:
                    source_translations[lang].update(
                        {k: v for k, v in tr_input.items() if v is not None}
                    )
                else:
                    source_translations[lang] = tr_input
            kwargs["translations"] = list(source_translations.values())

    @classmethod
    def create_event(cls, info, kwargs, *, source_event=None):
        """
        Create a new Event, optionally copying an existing event.
        Validates target projects, manages ticket system assignments, and
        copies image attachments if cloning.
        """
        original_kwargs = deepcopy(kwargs)

        project, event_group = cls.resolve_event_target(
            info, kwargs.pop("project_id"), kwargs.pop("event_group_id", None)
        )
        kwargs["project_id"] = project.pk
        if event_group:
            kwargs["event_group_id"] = event_group.pk

        if source_event is not None:
            for field in (
                "duration",
                "participants_per_invite",
                "capacity_per_occurrence",
                "ready_for_event_group_publishing",
            ):
                if field not in kwargs:
                    kwargs[field] = getattr(source_event, field)

            if "ticket_system" not in kwargs:
                kwargs["ticket_system"] = source_event.ticket_system
                kwargs["ticket_system_url"] = source_event.ticket_system_url
                kwargs["ticket_system_end_time"] = source_event.ticket_system_end_time

            cls._seed_translations(kwargs, source_event)

        ticket_system = kwargs.pop("ticket_system", None)
        if isinstance(ticket_system, dict):
            kwargs.update(
                {
                    "ticket_system": ticket_system.get("type"),
                    "ticket_system_url": ticket_system.get(
                        "url",
                        _DEFAULT_TICKET_SYSTEM_URL,
                    ),
                    "ticket_system_end_time": ticket_system.get("end_time"),
                }
            )
        elif ticket_system is not None:
            kwargs["ticket_system"] = ticket_system

        has_explicit_image = bool(kwargs.get("image"))
        event = Event.objects.create_translatable_object(**kwargs)

        if source_event is not None and not has_explicit_image:
            cls._copy_image_file(source_event, event)

        try:
            event.clean()
        except ValidationError as e:
            raise DataValidationError(str(e))

        logger.info(
            f"user {info.context.user.uuid} added event {event} "
            f"with data {original_kwargs}"
        )

        event.refresh_from_db()
        return event

    @classmethod
    def create_event_group(cls, info, kwargs, *, source_event_group=None):
        """
        Create a new EventGroup, optionally copying an existing event group.
        Validates project administration rights and copies image attachments if cloning.
        """
        original_kwargs = deepcopy(kwargs)
        user = info.context.user

        project = get_obj_if_user_can_administer(
            info, kwargs.pop("project_id"), Project
        )
        if not user.can_manage_event_groups_in_project(project):
            raise PermissionDenied()

        kwargs["project_id"] = project.pk

        if source_event_group is not None:
            cls._seed_translations(kwargs, source_event_group)

        has_explicit_image = bool(kwargs.get("image"))
        event_group = EventGroup.objects.create_translatable_object(**kwargs)

        if source_event_group is not None and not has_explicit_image:
            cls._copy_image_file(source_event_group, event_group)

        logger.info(
            f"user {user.uuid} added event group {event_group} "
            f"with data {original_kwargs}"
        )

        return event_group
