import html
import logging
import os
import re
from copy import deepcopy

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django_ilmoitin.dummy_context import dummy_context
from django_ilmoitin.models import NotificationTemplate, NotificationTemplateException
from django_ilmoitin.utils import RenderedTemplate, render_notification_template
from graphene.utils.str_converters import to_camel_case
from graphql_relay import from_global_id
from parler.utils.context import switch_language

from common.utils import (
    check_can_user_administer,
    get_obj_from_global_id,
    get_obj_if_user_can_administer,
    update_object,
    update_object_with_translations,
)
from events.consts import NotificationType
from events.enums import InvitationMessageFormat
from events.models import Enrolment, Event, EventGroup, Occurrence
from kukkuu.consts import DATA_VALIDATION_ERROR
from kukkuu.exceptions import (
    ApiUsageError,
    DataValidationError,
    ObjectDoesNotExistError,
    OccurrenceYearMismatchError,
    SingleEventsDisallowedError,
)
from kukkuu.utils import get_kukkuu_error_by_code
from languages.models import Language
from organisations.models import Organisation
from projects.models import Project
from reports.consts import CONTACT_LANGUAGE_TO_LANGUAGE
from tags.models import Accessibility, ThemePath
from users.cache import UserRequestCache
from venues.models import Venue
from venues.services import get_system_venue

logger = logging.getLogger(__name__)

_DEFAULT_TICKET_SYSTEM_URL = "https://example.com"
# Maximum value for a 16-bit signed integer (2^15 - 1), matching PostgreSQL
# `smallint` and Django's `PositiveSmallIntegerField` upper bound.
_POSITIVE_SMALL_INT_MAX = 32767
UNSET = object()


class EnrolmentAPIService:
    """Service class for enrolment arrival validation and updates."""

    @staticmethod
    def _should_use_explicit_counts(
        arrived_children_count: int | None,
        arrived_guardians_count: int | None,
    ) -> bool:
        has_children = arrived_children_count is not None
        has_guardians = arrived_guardians_count is not None
        if has_children != has_guardians:
            raise DataValidationError(
                "Both arrivedChildrenCount and arrivedGuardiansCount "
                "must be provided together."
            )
        return has_children and has_guardians

    @staticmethod
    def _apply_explicit_arrived_counts(
        enrolment: Enrolment,
        arrived_children_count: int,
        arrived_guardians_count: int,
        attended=UNSET,
    ) -> None:
        if arrived_children_count < 0 or arrived_guardians_count < 0:
            raise DataValidationError("Arrived participant counts cannot be negative.")
        if arrived_children_count > enrolment.booked_children_count:
            raise DataValidationError(
                f"Arrived children count ({arrived_children_count}) cannot exceed "
                f"booked children count ({enrolment.booked_children_count})."
            )
        if arrived_guardians_count > enrolment.booked_guardians_count:
            raise DataValidationError(
                f"Arrived guardians count ({arrived_guardians_count}) cannot exceed "
                f"booked guardians count ({enrolment.booked_guardians_count})."
            )

        derived_attended = (arrived_children_count + arrived_guardians_count) > 0
        if attended is not UNSET and attended is not derived_attended:
            raise DataValidationError(
                "Attended status contradicts the provided arrived participant counts."
            )

        enrolment.arrived_children_count = arrived_children_count
        enrolment.arrived_guardians_count = arrived_guardians_count
        enrolment.attended = derived_attended

    @staticmethod
    def _apply_attended_flag(enrolment: Enrolment, attended) -> None:
        if attended is UNSET:
            raise DataValidationError(
                '"attended" or arrived participant counts are required.'
            )
        if attended is True:
            enrolment.arrived_children_count = enrolment.booked_children_count
            enrolment.arrived_guardians_count = enrolment.booked_guardians_count
        elif attended is False:
            enrolment.arrived_children_count = 0
            enrolment.arrived_guardians_count = 0
        else:
            enrolment.arrived_children_count = None
            enrolment.arrived_guardians_count = None
        enrolment.attended = attended

    @classmethod
    def apply_arrival(
        cls,
        enrolment: Enrolment,
        *,
        attended=UNSET,
        arrived_children_count: int | None = None,
        arrived_guardians_count: int | None = None,
    ) -> Enrolment:
        """
        Validate and apply arrival counts and/or attended status to an enrolment.

        Supports either explicit (arrived_children_count, arrived_guardians_count)
        pairs (deriving `attended = (children + guardians) > 0`), or an `attended`
        boolean/null alone (defaulting counts to booked counts when True, 0 when False,
        and None when None).
        """
        if cls._should_use_explicit_counts(
            arrived_children_count, arrived_guardians_count
        ):
            cls._apply_explicit_arrived_counts(
                enrolment,
                arrived_children_count,
                arrived_guardians_count,
                attended=attended,
            )
        else:
            cls._apply_attended_flag(enrolment, attended)

        enrolment.save()
        return enrolment


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

    If ``events`` is given (e.g. the admin form's selected events), those are
    checked in-memory. Otherwise the event group's events are checked with a
    database query, bypassing any prefetch cache on the related manager so the
    check can't be skewed by stale or filtered prefetches.
    """
    project_id = (
        project.pk if project is not None else getattr(event_group, "project_id", None)
    )

    if events is not None:
        has_mismatch = any(event.project_id != project_id for event in events)
    elif event_group and event_group.pk:
        has_mismatch = (
            Event.objects.filter(event_group_id=event_group.pk)
            .exclude(project_id=project_id)
            .exists()
        )
    else:
        has_mismatch = False

    if has_mismatch:
        raise ValidationError(
            _("The event group and its events must belong to the same project."),
            code=DATA_VALIDATION_ERROR,
        )


def validate_registration_opens_at(registration_opens_at) -> None:
    """Validate the registration opening time given when publishing events."""
    if registration_opens_at is None:
        raise ValidationError(
            _("Registration opening time must be given a value."),
            code=DATA_VALIDATION_ERROR,
        )
    if timezone.is_naive(registration_opens_at):
        raise ValidationError(
            _("Registration opening time must include a timezone offset."),
            code=DATA_VALIDATION_ERROR,
        )
    if registration_opens_at < timezone.now():
        raise ValidationError(
            _("Registration opening time must be now or in the future."),
            code=DATA_VALIDATION_ERROR,
        )


def validate_registration_opens_at_is_not_before_published_at(
    *, registration_opens_at, published_at
) -> None:
    """Validate that registration opening time is not before publication time"""
    if (
        registration_opens_at is not None
        and published_at is not None
        and registration_opens_at < published_at
    ):
        raise ValidationError(
            _("Registration opening time must not be before publication time"),
            code=DATA_VALIDATION_ERROR,
        )


def sync_external_event_occurrence(event: Event) -> Occurrence | None:
    """
    Ensure an external ticket system event has one Occurrence matching
    its ticket_system_end_time, ticket_system_url, and the global system venue.
    """
    if not event.is_external_ticket_system_event or not event.ticket_system_end_time:
        return None

    system_venue = get_system_venue()

    translated_langs = list(event.translations.values_list("language_code", flat=True))
    default_lang = settings.LANGUAGE_CODE
    if default_lang in translated_langs:
        lang = default_lang
    elif translated_langs:
        lang = translated_langs[0]
    else:
        lang = default_lang

    occurrence = event.occurrences.first()
    if occurrence:
        occurrence.time = event.ticket_system_end_time
        occurrence.ticket_system_url = event.ticket_system_url
        occurrence.venue = system_venue
        occurrence.save(update_fields=["time", "ticket_system_url", "venue"])
    else:
        occurrence = Occurrence.objects.create(
            event=event,
            time=event.ticket_system_end_time,
            ticket_system_url=event.ticket_system_url,
            venue=system_venue,
        )
        occurrence.languages.set(
            [Language.objects.get(alpha_3_code=CONTACT_LANGUAGE_TO_LANGUAGE[lang])]
        )
    return occurrence


def sync_external_occurrence_to_event(occurrence: Occurrence) -> Event | None:
    """
    Sync an external ticket system event occurrence's time and URL back to its Event.
    """
    if not (occurrence.event and occurrence.event.is_external_ticket_system_event):
        return None

    event = occurrence.event
    event.ticket_system_end_time = occurrence.time
    if occurrence.ticket_system_url:
        event.ticket_system_url = occurrence.ticket_system_url
    event.save(update_fields=["ticket_system_end_time", "ticket_system_url"])
    return event


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
    def get_visible_ticket_system_url(event: Event, url: str, user) -> str | None:
        """
        Hide the external ticket system URL before the event's registration opens from
        users who can't administer the event.

        :return: None if the given event's registration is not open and the user can not
            administer the event, otherwise the given url.
        """
        if event.is_registration_open() or event.can_user_administer(user):
            return url
        return None

    class Resolver:
        """
        Resolves Relay Global IDs into model instances with permission checks.
        """

        @staticmethod
        def project(info, project_global_id: str) -> Project:
            """
            Resolve a Project by its global ID and verify administration
            permissions.
            """
            return get_obj_if_user_can_administer(info, project_global_id, Project)

        @staticmethod
        def event_group(info, event_group_global_id: str) -> EventGroup:
            """
            Resolve an EventGroup by its global ID and verify administration
            permissions.
            """
            return get_obj_if_user_can_administer(
                info, event_group_global_id, EventGroup
            )

        @staticmethod
        def organisation(info, organisation_global_id: str) -> Organisation:
            """
            Resolve an Organisation by global ID and verify user permission.
            """
            organisation = get_obj_from_global_id(
                info, organisation_global_id, Organisation
            )
            user = info.context.user
            if not (
                user.is_system_administrator
                or user.organisations.filter(id=organisation.id).exists()
            ):
                raise PermissionDenied(
                    "You do not have permission to assign events to this organisation."
                )
            return organisation

        @staticmethod
        def theme_paths(
            info, theme_path_global_ids: list[str] | None, source_event=None
        ) -> list[ThemePath]:
            """
            Resolve theme paths by global IDs. An omitted (None) list falls back
            to the theme paths of source event, if it is given. The result must
            not be empty.
            """
            if theme_path_global_ids is None and source_event is not None:
                theme_paths = list(source_event.theme_paths.all())
            else:
                theme_paths = [
                    get_obj_from_global_id(info, global_id, ThemePath)
                    for global_id in theme_path_global_ids or []
                ]
            if not theme_paths:
                raise DataValidationError("At least one theme path is required.")
            return theme_paths

        @classmethod
        def event_target(cls, info, project_global_id, event_group_global_id):
            """
            Resolve the target Project and EventGroup for a new event.
            Ensures the user has administration rights and validates project matching
            and single-event permissions.
            """
            project = cls.project(info, project_global_id)
            event_group = None
            if event_group_global_id:
                event_group = cls.event_group(info, event_group_global_id)
                if event_group.project_id != project.pk:
                    raise DataValidationError(
                        "Event group does not belong to the project."
                    )
            elif not project.single_events_allowed:
                raise SingleEventsDisallowedError(
                    f"Single events are disallowed in project {project}."
                )
            return project, event_group

        @staticmethod
        def event_organisation(
            info, organisation_global_id=None, source_event=None
        ) -> int:
            """
            Determine and validate the organisation PK for event creation.
            Uses explicit organisation_id if provided, source_event's organisation
            if cloning, or the user's sole organisation if only one exists.
            """
            if organisation_global_id:
                return EventAPIService.Resolver.organisation(
                    info, organisation_global_id
                ).pk
            if source_event is not None:
                return source_event.organisation_id

            user = info.context.user
            if user.organisations.count() == 1:
                return user.organisations.first().pk

            raise PermissionDenied("Organisation must be provided.")

    class Cleaner:
        """
        Normalizes and cleans GraphQL mutation input kwargs for Event models.
        """

        @classmethod
        def target(cls, info, kwargs: dict) -> None:
            project, event_group = EventAPIService.Resolver.event_target(
                info, kwargs.pop("project_id"), kwargs.pop("event_group_id", None)
            )
            kwargs["project_id"] = project.pk
            if event_group:
                kwargs["event_group_id"] = event_group.pk

        @classmethod
        def project_id(cls, info, kwargs: dict) -> None:
            if project_global_id := kwargs.pop("project_id", None):
                kwargs["project_id"] = EventAPIService.Resolver.project(
                    info, project_global_id
                ).pk

        @classmethod
        def event_group_id(cls, info, kwargs: dict) -> None:
            if event_group_global_id := kwargs.pop("event_group_id", None):
                kwargs["event_group_id"] = EventAPIService.Resolver.event_group(
                    info, event_group_global_id
                ).pk

        @classmethod
        def organisation_id(cls, info, kwargs: dict) -> None:
            if organisation_global_id := kwargs.pop("organisation_id", None):
                kwargs["organisation_id"] = EventAPIService.Resolver.organisation(
                    info, organisation_global_id
                ).pk

        @staticmethod
        def create_ticket_system(kwargs: dict) -> None:
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

        @staticmethod
        def update_ticket_system(kwargs: dict) -> None:
            if ticket_system := kwargs.pop("ticket_system", None):
                if "url" in ticket_system:
                    kwargs["ticket_system_url"] = ticket_system.get("url", "")
                if "end_time" in ticket_system:
                    kwargs["ticket_system_end_time"] = ticket_system.get("end_time")

    @classmethod
    def _seed_source_event_data(cls, kwargs: dict, source_event: Event) -> None:
        """
        Seed omitted scalars, ticket system, and translations from source event.
        """
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
            submitted = kwargs.get("translations") or []
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

        cls.Cleaner.target(info, kwargs)
        kwargs["organisation_id"] = cls.Resolver.event_organisation(
            info, kwargs.pop("organisation_id", None), source_event=source_event
        )
        theme_paths = cls.Resolver.theme_paths(
            info, kwargs.pop("theme_path_ids", None), source_event=source_event
        )
        if source_event is not None:
            cls._seed_source_event_data(kwargs, source_event)
        cls.Cleaner.create_ticket_system(kwargs)

        has_explicit_image = bool(kwargs.get("image"))
        try:
            event = Event.objects.create_translatable_object(**kwargs)
            event.theme_paths.set(theme_paths)
            if source_event is not None and not has_explicit_image:
                cls._copy_image_file(source_event, event)
            event.clean()
            sync_external_event_occurrence(event)
        except ValidationError as e:
            raise DataValidationError(str(e))

        logger.info(
            f"user {info.context.user.uuid} added event {event} "
            f"with data {original_kwargs}"
        )

        event.refresh_from_db()
        return event

    @classmethod
    def update_event(cls, info, kwargs):
        """
        Update an existing Event.
        Validates administration rights, resolves target relations, updates
        translations, and cleans the model instance.
        """
        original_kwargs = deepcopy(kwargs)

        event = get_obj_if_user_can_administer(info, kwargs.pop("id"), Event)
        cls.Cleaner.project_id(info, kwargs)
        cls.Cleaner.event_group_id(info, kwargs)
        cls.Cleaner.organisation_id(info, kwargs)
        cls.Cleaner.update_ticket_system(kwargs)
        theme_path_ids = kwargs.pop("theme_path_ids", None)
        theme_paths = (
            None
            if theme_path_ids is None
            else cls.Resolver.theme_paths(info, theme_path_ids)
        )

        try:
            update_object_with_translations(event, kwargs)
            if theme_paths is not None:
                event.theme_paths.set(theme_paths)
            event.clean()
            sync_external_event_occurrence(event)
        except ValidationError as e:
            raise DataValidationError(str(e))

        logger.info(
            f"user {info.context.user.uuid} updated event {event} "
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

        project = cls.Resolver.project(info, kwargs.pop("project_id"))
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

    @staticmethod
    def _render_invitation_template(
        event_group: EventGroup, language: str
    ) -> RenderedTemplate | None:
        """
        Render the EVENT_GROUP_PUBLISHED notification template for the given
        event group and language without unsubscribe or per-child event group URLs.
        """
        template = NotificationTemplate.objects.filter(
            type=NotificationType.EVENT_GROUP_PUBLISHED
        ).first()
        if not template:
            return None

        context = {
            **(dummy_context.get(NotificationType.EVENT_GROUP_PUBLISHED) or {}),
            "event_group": event_group,
            "is_sending_email": False,
            "unsubscribe_url": None,
        }
        context.pop("event_group_url", None)
        try:
            return render_notification_template(
                template, context=context, language_code=language
            )
        except (NotificationTemplateException, ObjectDoesNotExist):
            return None

    @staticmethod
    def _format_invitation_html(rendered: RenderedTemplate) -> str:
        """
        Return the trimmed HTML body of a rendered invitation notification.
        """
        return rendered.body_html.strip()

    @staticmethod
    def _format_invitation_text(rendered: RenderedTemplate) -> str:
        """
        Return the plain-text body of a rendered invitation notification with
        HTML entities unescaped and wrapped lines collapsed per paragraph.
        """
        paragraphs = [
            " ".join(paragraph.split())
            for paragraph in re.split(r"\n\s*\n", html.unescape(rendered.body_text))
        ]
        return "\n".join(p for p in paragraphs if p)

    @classmethod
    def get_invitation_message(
        cls,
        event_group: EventGroup,
        *,
        message_format: InvitationMessageFormat = InvitationMessageFormat.TEXT,
        language: str | None = None,
    ) -> str | None:
        """
        Render the event group's invitation letter from the EVENT_GROUP_PUBLISHED
        notification template in the requested format (TEXT or HTML).
        Falls back to event_group.description (or None if empty) when no template
        exists or rendering fails.
        """
        lang = (language or get_language() or settings.LANGUAGE_CODE).split("-")[0]
        if lang not in settings.PARLER_SUPPORTED_LANGUAGE_CODES:
            lang = settings.LANGUAGE_CODE

        with switch_language(event_group, lang):
            fallback = (
                event_group.safe_translation_getter("description", any_language=True)
                or None
            )
            rendered = cls._render_invitation_template(event_group, lang)
            if not rendered:
                return fallback

            if message_format == InvitationMessageFormat.HTML:
                return cls._format_invitation_html(rendered) or fallback

            return cls._format_invitation_text(rendered) or fallback


class OccurrenceAPIService:
    """
    Service class for Occurrence GraphQL API business logic.
    """

    NON_NULLABLE_UPDATE_FIELDS = ("time",)
    ATTENDED_OVERRIDE_FIELDS = (
        "attended_children_count_override",
        "attended_adults_count_override",
    )

    @staticmethod
    def check_can_user_administer(occurrence: Occurrence, info) -> None:
        """
        Verify the request's user can administer the given occurrence, using the
        request-scoped organisation IDs cache to avoid N+1 database queries.
        """
        if not occurrence.can_user_administer(
            info.context.user,
            user_organisation_ids=UserRequestCache.get_organisation_ids(info),
        ):
            raise PermissionDenied()

    class Resolver:
        """
        Resolves Relay Global IDs into model instances with permission checks.
        """

        @staticmethod
        def event_id_for_create(info, event_global_id: str) -> int:
            return get_obj_if_user_can_administer(info, event_global_id, Event).pk

        @staticmethod
        def venue_id_for_create(info, venue_global_id: str) -> int:
            return get_obj_if_user_can_administer(info, venue_global_id, Venue).pk

        @staticmethod
        def event_id_for_update(
            info, occurrence: Occurrence, raw_event_id: str | None
        ) -> int | None:
            if raw_event_id is None:
                return None
            requested_id = from_global_id(raw_event_id).id
            if occurrence.event.is_external_ticket_system_event:
                if requested_id != str(occurrence.event_id):
                    raise ApiUsageError(
                        _("Cannot reassign an external ticket system event occurrence.")
                    )
                return None
            return get_obj_if_user_can_administer(info, raw_event_id, Event).pk

        @staticmethod
        def venue_id_for_update(
            info, occurrence: Occurrence, raw_venue_id: str | None
        ) -> int | None:
            if raw_venue_id is None:
                return None
            requested_id = from_global_id(raw_venue_id).id
            if occurrence.event.is_external_ticket_system_event:
                if requested_id != str(occurrence.venue_id):
                    raise ApiUsageError(
                        _(
                            "Cannot change the venue of an external ticket system "
                            "event occurrence."
                        )
                    )
                return None
            venue = get_obj_from_global_id(info, raw_venue_id, Venue)
            if venue.is_system:
                raise ApiUsageError(_("Internal events cannot use the system venue."))
            check_can_user_administer(venue, info.context.user)
            return venue.pk

        @staticmethod
        def accessibilities(
            info, accessibility_ids: list[str] | None
        ) -> list[Accessibility] | None:
            if accessibility_ids is None:
                return None
            return [
                get_obj_from_global_id(info, global_id, Accessibility)
                for global_id in accessibility_ids
            ]

        @staticmethod
        def languages(info, language_ids: list[str] | None) -> list[Language]:
            if not language_ids:
                raise DataValidationError(
                    _("An occurrence needs at least one language.")
                )
            languages = [
                get_obj_from_global_id(info, global_id, Language)
                for global_id in language_ids
            ]
            for language in languages:
                if not language.can_be_occurrence_language:
                    raise DataValidationError(
                        f'Language "{language.alpha_3_code}" can not be chosen as an '
                        "occurrence language."
                    )
            return languages

    class Cleaner:
        """
        Normalizes and cleans GraphQL mutation input kwargs for Occurrence models.
        """

        @classmethod
        def _resolve_foreign_keys(
            cls, info, occurrence: Occurrence, kwargs: dict
        ) -> None:
            if "event_id" in kwargs:
                resolved_event_id = OccurrenceAPIService.Resolver.event_id_for_update(
                    info, occurrence, kwargs["event_id"]
                )
                if resolved_event_id is not None:
                    kwargs["event_id"] = resolved_event_id
                else:
                    kwargs.pop("event_id")

            if "venue_id" in kwargs:
                resolved_venue_id = OccurrenceAPIService.Resolver.venue_id_for_update(
                    info, occurrence, kwargs["venue_id"]
                )
                if resolved_venue_id is not None:
                    kwargs["venue_id"] = resolved_venue_id
                else:
                    kwargs.pop("venue_id")

        @classmethod
        def prepare_update_kwargs(
            cls, info, occurrence: Occurrence, kwargs: dict
        ) -> None:
            cls._resolve_foreign_keys(info, occurrence, kwargs)

            for field in OccurrenceAPIService.NON_NULLABLE_UPDATE_FIELDS:
                if field in kwargs and kwargs[field] is None:
                    kwargs.pop(field)

            ticket_system_url = kwargs.pop("ticket_system", {}).get("url")
            if ticket_system_url is not None:
                kwargs["ticket_system_url"] = ticket_system_url

    class Validator:
        """
        Validates occurrence mutation inputs and constraints.
        """

        @staticmethod
        def _resolve_and_validate_event(
            kwargs: dict, occurrence: Occurrence | None = None
        ) -> Event | None:
            if occurrence:
                event = occurrence.event
                if (
                    event.is_external_ticket_system_event
                    and kwargs.get("capacity_override") is not None
                ):
                    raise ApiUsageError(
                        _(
                            "Cannot set capacity override on an external ticket system "
                            "event occurrence."
                        )
                    )
                if event.is_external_ticket_system_event and any(
                    kwargs.get(field) is not None
                    for field in OccurrenceAPIService.ATTENDED_OVERRIDE_FIELDS
                ):
                    raise ApiUsageError(
                        _(
                            "Cannot set attended count override on an external ticket "
                            "system event occurrence."
                        )
                    )
                return event

            event_id = kwargs.get("event_id")
            if not event_id:
                return None

            try:
                event = Event.objects.get(pk=event_id)
            except Event.DoesNotExist as e:
                raise ObjectDoesNotExistError(e)

            if event.is_external_ticket_system_event:
                raise ApiUsageError(
                    _(
                        "Cannot add occurrences to an external ticket system event; "
                        "its single occurrence is created automatically. Use "
                        "updateOccurrence to edit it."
                    )
                )
            return event

        @staticmethod
        def _validate_time_year(
            kwargs: dict,
            occurrence: Occurrence | None = None,
            event: Event | None = None,
        ) -> None:
            time = kwargs.get("time")
            if not time:
                return

            if occurrence:
                existing_occurrences = occurrence.event.occurrences.exclude(
                    pk=occurrence.pk
                )
            elif event:
                existing_occurrences = event.occurrences.all()
            else:
                existing_occurrences = Occurrence.objects.none()

            if (
                existing_occurrences.exists()
                and not existing_occurrences.filter(time__year=time.year).exists()
            ):
                raise OccurrenceYearMismatchError(
                    _(
                        "The occurrence year must match the other occurrences of the "
                        "event."
                    )
                )

        @staticmethod
        def _validate_attended_count_overrides(
            kwargs: dict, occurrence: Occurrence | None = None
        ) -> None:
            fields = OccurrenceAPIService.ATTENDED_OVERRIDE_FIELDS
            for field in fields:
                value = kwargs.get(field)
                if value is not None and not 0 <= value <= _POSITIVE_SMALL_INT_MAX:
                    raise DataValidationError(
                        f"{to_camel_case(field)} must be between 0 and "
                        f"{_POSITIVE_SMALL_INT_MAX}."
                    )

            # Resulting state after the update: omitted keys keep the stored
            # value, an explicit null clears it. This must run before the object
            # is saved, otherwise the DB check constraint fires first.
            resulting = [
                kwargs[field] if field in kwargs else getattr(occurrence, field, None)
                for field in fields
            ]
            if (resulting[0] is None) != (resulting[1] is None):
                raise DataValidationError(
                    "attendedChildrenCountOverride and attendedAdultsCountOverride "
                    "must both be set or both be null."
                )

        @classmethod
        def validate_input(
            cls, kwargs: dict, occurrence: Occurrence | None = None
        ) -> None:
            event = cls._resolve_and_validate_event(kwargs, occurrence=occurrence)
            cls._validate_time_year(kwargs, occurrence=occurrence, event=event)
            cls._validate_attended_count_overrides(kwargs, occurrence)

        @staticmethod
        def clean_occurrence(occurrence: Occurrence) -> None:
            try:
                occurrence.clean()
            except ValidationError as e:
                kukkuu_error = get_kukkuu_error_by_code(getattr(e, "code", None))
                if kukkuu_error:
                    raise kukkuu_error(e.message)
                raise DataValidationError(str(e))

    @classmethod
    def create_occurrence(cls, info, kwargs: dict) -> Occurrence:
        original_kwargs = deepcopy(kwargs)

        kwargs["event_id"] = cls.Resolver.event_id_for_create(info, kwargs["event_id"])
        kwargs["venue_id"] = cls.Resolver.venue_id_for_create(info, kwargs["venue_id"])

        ticket_system_url = kwargs.pop("ticket_system", {}).get("url")
        if ticket_system_url is not None:
            kwargs["ticket_system_url"] = ticket_system_url

        accessibilities = cls.Resolver.accessibilities(
            info, kwargs.pop("accessibility_ids", None) or []
        )
        languages = cls.Resolver.languages(info, kwargs.pop("language_ids", None))

        cls.Validator.validate_input(kwargs)
        occurrence = Occurrence(**kwargs)
        cls.Validator.clean_occurrence(occurrence)
        occurrence.save()
        occurrence.languages.set(languages)
        if accessibilities:
            occurrence.accessibilities.set(accessibilities)

        # needed because enrolment_count is an annotated field
        occurrence.enrolment_count = 0
        occurrence.calculated_attended_seats = 0
        occurrence.attended_seats = 0
        occurrence.handled_enrolment_count = 0
        occurrence.pending_arrival_seats = 0

        logger.info(
            f"user {info.context.user.uuid} added occurrence {occurrence} with data "
            f"{original_kwargs}"
        )
        return occurrence

    @classmethod
    def update_occurrence(cls, info, kwargs: dict) -> Occurrence:
        original_kwargs = deepcopy(kwargs)
        occurrence = get_obj_if_user_can_administer(info, kwargs.pop("id"), Occurrence)

        cls.Cleaner.prepare_update_kwargs(info, occurrence, kwargs)
        accessibilities = cls.Resolver.accessibilities(
            info, kwargs.pop("accessibility_ids", None)
        )
        language_ids = kwargs.pop("language_ids", None)
        languages = (
            None if language_ids is None else cls.Resolver.languages(info, language_ids)
        )

        cls.Validator.validate_input(kwargs, occurrence=occurrence)
        update_object(occurrence, kwargs)
        if accessibilities is not None:
            occurrence.accessibilities.set(accessibilities)
        if languages is not None:
            occurrence.languages.set(languages)

        cls.Validator.clean_occurrence(occurrence)
        sync_external_occurrence_to_event(occurrence)

        logger.info(
            f"user {info.context.user.uuid} updated occurrence {occurrence} "
            f"of event {occurrence.event} with data {original_kwargs}"
        )
        return occurrence
