import logging
from datetime import timedelta
from typing import Callable, Optional

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Count, Q, Sum, UniqueConstraint, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from helsinki_gdpr.models import SerializableMixin
from parler.models import TranslatedFields

import events.notification_service as notification_service
from children.models import Child
from common.decorators import execute_in_background
from common.models import TimestampedModel, TranslatableModel
from common.utils import get_translations_dict, year_of
from events.consts import MIN_SEATS_PER_ENROLMENT, NotificationType
from events.enums import EnrolmentDeniedReason
from events.exceptions import PasswordAlreadyAssignedError
from events.managers import (
    EnrolmentQueryset,
    EventGroupQueryset,
    EventQueryset,
    OccurrenceQueryset,
    TicketSystemPasswordQueryset,
)
from kukkuu.consts import (
    DATA_VALIDATION_ERROR,
    EVENT_GROUP_ALREADY_PUBLISHED_ERROR,
    EVENT_GROUP_NOT_READY_FOR_PUBLISHING_ERROR,
    TICKET_SYSTEM_URL_MISSING_ERROR,
)
from kukkuu.exceptions import IllegalEnrolmentReferenceId
from kukkuu.service import get_hashid_service
from venues.models import Venue

logger = logging.getLogger(__name__)

_MISSING = object()


def _both_or_neither_constraint(
    field_a: str, field_b: str, name: str
) -> models.CheckConstraint:
    """
    Return a CheckConstraint requiring two nullable columns to be both NULL or
    both non-NULL.
    """
    return models.CheckConstraint(
        condition=(
            Q(**{f"{field_a}__isnull": True, f"{field_b}__isnull": True})
            | Q(**{f"{field_a}__isnull": False, f"{field_b}__isnull": False})
        ),
        name=name,
    )


class _SeatMetricsRollupMixin:
    """Shared metric rollup methods summing across a model's child queryset."""

    def _metric_children(self):
        raise NotImplementedError

    def _sum_children_metric(
        self, method_name: str, *, external_zero: bool = False
    ) -> int:
        if external_zero and getattr(self, "is_external_ticket_system_event", False):
            return 0
        return sum(
            getattr(child, method_name)() for child in self._metric_children().all()
        )

    def get_enrolment_count(self) -> int:
        return self._sum_children_metric("get_enrolment_count")

    def get_enrolled_children_count(self) -> int:
        return self._sum_children_metric("get_enrolled_children_count")

    def get_enrolled_adults_count(self) -> int:
        return self._sum_children_metric("get_enrolled_adults_count")

    def get_attended_enrolment_count(self) -> int:
        return self._sum_children_metric("get_attended_enrolment_count")

    def get_attended_children_count(self) -> int:
        return self._sum_children_metric(
            "get_attended_children_count", external_zero=True
        )

    def get_attended_adults_count(self) -> int:
        return self._sum_children_metric(
            "get_attended_adults_count", external_zero=True
        )

    def get_attended_seats(self) -> int:
        """
        Return the total effective arrived physical seats summed across all
        children (0 for external ticket system events).
        """
        return self._sum_children_metric("get_attended_seats", external_zero=True)

    def get_capacity(self) -> Optional[int]:
        if getattr(self, "is_external_ticket_system_event", False):
            return 0
        try:
            return self._sum_children_metric("get_capacity")
        except TypeError:
            return None

    def get_reserved_seats(self) -> int:
        return self._sum_children_metric("get_reserved_seats")


class EventGroup(
    _SeatMetricsRollupMixin, TimestampedModel, TranslatableModel, SerializableMixin
):
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=255, blank=True),
        short_description=models.TextField(
            verbose_name=_("short description"), blank=True
        ),
        description=models.TextField(verbose_name=_("description"), blank=True),
        image_alt_text=models.CharField(
            verbose_name=_("image alt text"), blank=True, max_length=255
        ),
    )
    image = models.ImageField(blank=True, verbose_name=_("image"))
    published_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("published at")
    )
    project = models.ForeignKey(
        "projects.Project",
        verbose_name=_("project"),
        related_name="event_groups",
        on_delete=models.CASCADE,
    )

    serialize_fields = [{"name": "name_with_translations"}, {"name": "project"}]

    objects = SerializableMixin.SerializableManager.from_queryset(EventGroupQueryset)()

    class Meta:
        verbose_name = _("event group")
        verbose_name_plural = _("event groups")
        ordering = ("id",)

    @property
    def name_with_translations(self):
        return get_translations_dict(self, "name")

    def __str__(self):
        name = self.safe_translation_getter("name", super().__str__())
        published_text = _("published") if self.published_at else _("unpublished")
        return f"{name} ({self.pk}) ({self.project.year}) ({published_text})"

    def can_user_administer(self, user):
        return user.can_administer_project(self.project)

    def can_user_publish(
        self, user, user_organisation_ids: Optional[set] = None
    ) -> bool:
        """
        Check if the given user can publish this event group.
        Requires project publish rights AND (system admin OR membership in the
        organisations of all unpublished events that will be published).
        """
        if not user or not user.is_authenticated:
            return False
        if not user.can_publish_in_project(self.project):
            return False
        if user.is_system_administrator:
            return True

        unpublished_events = self.events.unpublished()
        if not unpublished_events.exists():
            return True

        if user_organisation_ids is not None:
            return not unpublished_events.exclude(
                organisation_id__in=user_organisation_ids
            ).exists()
        return not unpublished_events.exclude(
            organisation__in=user.organisations.all()
        ).exists()

    def _get_enrolment_year(self) -> Optional[int]:
        """
        Determine the calendar year of this event group for enrolment quotas.

        Uses pre-annotated `_group_year` if present, falling back to the year
        of the earliest occurrence or external event publish date.
        """
        if hasattr(self, "_group_year"):
            return self._group_year
        if (
            occurrence := Occurrence.objects.filter(
                event__event_group=self,
                event__ticket_system=Event.INTERNAL,
            )
            .order_by("time")
            .first()
        ):
            return year_of(occurrence.time)
        external_event = (
            self.events.exclude(published_at=None)
            .exclude(ticket_system=Event.INTERNAL)
            .order_by("published_at", "id")
            .first()
        )
        return year_of(external_event.published_at) if external_event else None

    def _is_registration_open(self) -> bool:
        """
        Check if registration is open for events in this event group.

        Returns False if every published event in the group has a registration
        opening time and all of those opening times are in the future; True otherwise.
        """
        # A null registration_opens_at means no limitation, and unpublished events
        # can't be enrolled to. The registration is not open if every published event
        # has a registration opening time and their earliest one is in the future.
        if (
            hasattr(self, "_published_event_count")
            and hasattr(self, "_published_with_opening_time_count")
            and hasattr(self, "_earliest_opening_time")
        ):
            total = self._published_event_count
            with_opening_time = self._published_with_opening_time_count
            earliest_opening_time = self._earliest_opening_time
        else:
            stats = self.events.published().aggregate(
                total=Count("pk"),
                with_opening_time=Count("registration_opens_at"),
                earliest_opening_time=models.Min("registration_opens_at"),
            )
            total = stats["total"]
            with_opening_time = stats["with_opening_time"]
            earliest_opening_time = stats["earliest_opening_time"]

        return not (
            total > 0
            and total == with_opening_time
            and earliest_opening_time > timezone.now()
        )

    def get_enrolment_denied_reason(self, child: Child) -> None | EnrolmentDeniedReason:
        """
        Why, if for any reason, the given child can't enrol to an event
        in this event group?

        :return: None if the child can enrol, otherwise the reason why not.
        """
        # Unpublished event groups cannot be enrolled in.
        if not self.is_published():
            return EnrolmentDeniedReason.EVENT_GROUP_NOT_PUBLISHED

        # The child must belong to the same project as the event group.
        if child.project_id != self.project_id:
            return EnrolmentDeniedReason.CHILD_NOT_IN_EVENT_GROUP_PROJECT

        # An event group must have at least one occurrence or published external event.
        year = self._get_enrolment_year()
        if year is None:
            return EnrolmentDeniedReason.EMPTY_EVENT_GROUP

        # Check whether the child has reached the project's annual enrolment quota.
        if child.get_enrolment_count(year=year) >= child.project.enrolment_limit:
            return EnrolmentDeniedReason.YEARLY_ENROLMENT_LIMIT_REACHED

        # A child can only participate in one internal event per event group.
        if self.id in child.get_enrolled_event_group_ids():
            return EnrolmentDeniedReason.ALREADY_JOINED_EVENT_GROUP

        # A child can only receive one external ticket password per event group.
        if self.id in child.get_ticket_system_password_event_group_ids():
            return EnrolmentDeniedReason.ALREADY_HAS_PASSWORD_TO_EVENT_GROUP

        # At least one published event in the group must have open registration.
        if not self._is_registration_open():
            return EnrolmentDeniedReason.REGISTRATION_NOT_OPEN

        return None

    def can_child_enroll(self, child: Child) -> bool:
        """Check if the child can enroll to an event in the event group."""
        return self.get_enrolment_denied_reason(child) is None

    @execute_in_background(thread_name="eventgroup-notification-sender", daemonic=False)
    def _send_event_group_notifications_to_guardians_in_background(
        self, *args, **kwargs
    ):
        logger.info(
            "The sending of the event group publishing notification "
            "will be executed in background!"
        )
        notification_service.send_event_group_notifications_to_guardians(
            *args, **kwargs
        )

    def publish(self, *, registration_opens_at, send_notifications=True):
        """
        Publish the event group and its unpublished events.

        The registration opening time is set only to the unpublished events,
        the already published events are left unchanged. Republishing an already
        published event group without unpublished events is not allowed.
        """
        from events.services import validate_registration_opens_at

        unpublished_events = self.events.unpublished()
        if self.is_published() and not unpublished_events:
            raise ValidationError(
                "Event group is already published.",
                code=EVENT_GROUP_ALREADY_PUBLISHED_ERROR,
            )
        if any(not e.ready_for_event_group_publishing for e in unpublished_events):
            raise ValidationError(
                "All events are not ready for event group publishing.",
                code=EVENT_GROUP_NOT_READY_FOR_PUBLISHING_ERROR,
            )
        validate_registration_opens_at(registration_opens_at)

        with transaction.atomic():
            self.published_at = timezone.now()
            self.save()

            for event in unpublished_events:
                event._mark_published(registration_opens_at)
            logger.debug(
                "The atomic transaction to mark events of the group published "
                "has now finished."
            )

        if send_notifications:
            self._send_event_group_notifications_to_guardians_in_background(
                self,
                NotificationType.EVENT_GROUP_PUBLISHED,
                list(self.project.children.prefetch_related("guardians")),
                # Pass the used registration_opens_at value to email template context:
                registration_opens_at=registration_opens_at,
            )

    def is_published(self):
        return bool(self.published_at)

    def _metric_children(self):
        return self.events

    def clean(self):
        from events.services import validate_event_group_and_events_project_match

        validate_event_group_and_events_project_match(self)
        super().clean()

    def save(self, *args, **kwargs):
        from events.services import validate_event_group_and_events_project_match

        validate_event_group_and_events_project_match(self)
        super().save(*args, **kwargs)


class Event(
    _SeatMetricsRollupMixin, TimestampedModel, TranslatableModel, SerializableMixin
):
    CHILD_AND_GUARDIAN = "child_and_guardian"
    FAMILY = "family"
    PARTICIPANTS_PER_INVITE_CHOICES = (
        (CHILD_AND_GUARDIAN, _("Child and guardian")),
        (FAMILY, _("Family")),
    )

    # participants_per_invite -> (max extra children, max extra guardians)
    MAX_EXTRA_PARTICIPANTS = {
        CHILD_AND_GUARDIAN: (0, 0),
        FAMILY: (3, 1),
    }

    INTERNAL = "internal"
    TICKETMASTER = "ticketmaster"
    LIPPUPISTE = "lippupiste"
    TIXLY = "tixly"
    EXTERNAL_TICKET_SYSTEM_CHOICES = (
        (TICKETMASTER, _("Ticketmaster")),
        (LIPPUPISTE, _("Lippupiste")),
        (TIXLY, _("Tixly")),
    )
    TICKET_SYSTEM_CHOICES = ((INTERNAL, _("Internal")), *EXTERNAL_TICKET_SYSTEM_CHOICES)

    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=255, blank=True),
        short_description=models.TextField(
            verbose_name=_("short description"), blank=True
        ),
        description=models.TextField(verbose_name=_("description"), blank=True),
        image_alt_text=models.CharField(
            verbose_name=_("image alt text"), blank=True, max_length=255
        ),
    )
    image = models.ImageField(blank=True, verbose_name=_("image"))
    participants_per_invite = models.CharField(
        max_length=255,
        choices=PARTICIPANTS_PER_INVITE_CHOICES,
        verbose_name=_("participants per invite"),
    )
    duration = models.PositiveSmallIntegerField(
        verbose_name=_("duration"), blank=True, null=True, help_text=_("In minutes")
    )
    capacity_per_occurrence = models.PositiveSmallIntegerField(
        verbose_name=_("capacity per occurrence"),
        null=True,
        blank=True,
        help_text=_(
            "Total physical seat capacity. Each enrolment takes at least 2 seats "
            "(1 child + 1 guardian)."
        ),
    )
    published_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("published at")
    )
    registration_opens_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("registration opens at")
    )

    project = models.ForeignKey(
        "projects.Project",
        verbose_name=_("project"),
        related_name="events",
        on_delete=models.CASCADE,
    )
    event_group = models.ForeignKey(
        EventGroup,
        verbose_name=_("event group"),
        related_name="events",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    ready_for_event_group_publishing = models.BooleanField(
        verbose_name=_("ready for event group publishing"), default=False
    )
    ticket_system = models.CharField(
        max_length=32,
        choices=TICKET_SYSTEM_CHOICES,
        verbose_name=_("ticket system"),
        default=INTERNAL,
    )
    ticket_system_url = models.URLField(verbose_name=_("ticket system URL"), blank=True)
    # Note: ticket_system_end_time is deprecated in favor of the occurrence time of
    # the external event's single occurrence. Kept for backwards compatibility and
    # bidirectional sync until external occurrences are fully adopted.
    ticket_system_end_time = models.DateTimeField(
        verbose_name=_("ticket system end time"), blank=True, null=True
    )
    organisation = models.ForeignKey(
        "organisations.Organisation",
        verbose_name=_("organisation"),
        related_name="events",
        on_delete=models.PROTECT,
    )
    theme_paths = models.ManyToManyField(
        "tags.ThemePath",
        through="EventThemePath",
        verbose_name=_("theme paths"),
        related_name="events",
        blank=True,
    )

    serialize_fields = (
        {"name": "name_with_translations"},
        {"name": "event_group"},
        {"name": "project"},
        {"name": "organisation"},
        {"name": "ticket_system"},
    )

    objects = SerializableMixin.SerializableManager.from_queryset(EventQueryset)()

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")
        ordering = ["created_at", "id"]

    def __str__(self):
        name = self.safe_translation_getter("name", super().__str__())
        published_text = _("published") if self.published_at else _("unpublished")
        return f"{name} ({self.pk}) ({self.project.year}) ({published_text})"

    @property
    def name_with_translations(self):
        return get_translations_dict(self, "name")

    @property
    def is_external_ticket_system_event(self):
        return any(
            self.ticket_system == choice[0]
            for choice in self.EXTERNAL_TICKET_SYSTEM_CHOICES
        )

    def clean(self):
        from events.services import validate_event_and_event_group_project_match

        validate_event_and_event_group_project_match(self)

        if self.ticket_system == Event.INTERNAL:
            if self.capacity_per_occurrence is None:
                raise ValidationError(
                    _(
                        "Capacity per occurrence is required when ticket system is "
                        "internal."
                    ),
                    code=DATA_VALIDATION_ERROR,
                )
        elif self.is_external_ticket_system_event:
            if not self.ticket_system_url:
                raise ValidationError(
                    _(
                        "Ticket system URL is required when ticket system is "
                        "any of the external ticket systems."
                    ),
                    code=TICKET_SYSTEM_URL_MISSING_ERROR,
                )
            if not self.ticket_system_end_time:
                raise ValidationError(
                    {
                        "ticket_system_end_time": _(
                            "Ticket system end time is required for external ticket "
                            "system events."
                        )
                    },
                    code=DATA_VALIDATION_ERROR,
                )

    def save(self, *args, **kwargs):
        from events.services import (
            validate_event_and_event_group_project_match,
            validate_registration_opens_at_is_not_before_published_at,
        )

        validate_event_and_event_group_project_match(self)
        validate_registration_opens_at_is_not_before_published_at(
            registration_opens_at=self.registration_opens_at,
            published_at=self.published_at,
        )

        try:
            old_capacity_per_occurrence = Event.objects.get(
                pk=self.pk
            ).capacity_per_occurrence
        except Event.DoesNotExist:
            old_capacity_per_occurrence = None

        super().save(*args, **kwargs)

        # This event's occurrences might get their capacity from this event, so here it
        # can be potentially changed if capacity per occurrence has been increased.
        if (
            old_capacity_per_occurrence is not None
            and self.capacity_per_occurrence is not None
            and self.capacity_per_occurrence > old_capacity_per_occurrence
        ):
            self.occurrences.send_free_spot_notifications_if_needed()

    def can_user_administer(
        self, user, user_organisation_ids: Optional[set] = None
    ) -> bool:
        """
        Check if the given user can administer (edit/delete) this event.
        Requires project admin rights AND (system admin OR membership in the event's
        organisation).
        """
        if not user or not user.is_authenticated:
            return False
        if not user.can_administer_project(self.project):
            return False
        if user.is_system_administrator:
            return True
        if user_organisation_ids is not None:
            return self.organisation_id in user_organisation_ids
        return user.organisations.filter(id=self.organisation_id).exists()

    def can_user_publish(
        self, user, user_organisation_ids: Optional[set] = None
    ) -> bool:
        """
        Check if the given user can publish this event.
        Requires project publish rights AND (system admin OR membership in the event's
        organisation).
        """
        if not user or not user.is_authenticated:
            return False
        if not user.can_publish_in_project(self.project):
            return False
        if user.is_system_administrator:
            return True
        if user_organisation_ids is not None:
            return self.organisation_id in user_organisation_ids
        return user.organisations.filter(id=self.organisation_id).exists()

    def _get_enrolment_year(self) -> Optional[int]:
        """
        Determine the calendar year of this event for enrolment quota checks.

        Returns the publish year for external ticketing systems, pre-annotated
        `_first_occurrence_year` if present, or the year of the earliest occurrence.
        """
        if self.ticket_system != Event.INTERNAL:
            # For external ticket system events published_at field is used to determine
            # the event's year. That is obviously not a perfect solution, but the best
            # we can do with the current data, and most probably good enough.
            return year_of(self.published_at)
        if hasattr(self, "_first_occurrence_year"):
            return self._first_occurrence_year
        occurrence = Occurrence.objects.filter(event=self).order_by("time").first()
        return year_of(occurrence.time) if occurrence else None

    def get_enrolment_denied_reason(self, child: Child) -> None | EnrolmentDeniedReason:
        """
        Why, if for any reason, the given child can't enrol to this event?

        :return: None if the child can enrol, otherwise the reason why not.
        """
        # Unpublished events cannot be enrolled in.
        if not self.is_published():
            return EnrolmentDeniedReason.EVENT_NOT_PUBLISHED

        # Enrolment is only allowed once the event's registration window has opened.
        if not self.is_registration_open():
            return EnrolmentDeniedReason.REGISTRATION_NOT_OPEN

        # The child must belong to the same project as the event.
        if child.project_id != self.project_id:
            return EnrolmentDeniedReason.CHILD_NOT_IN_EVENT_PROJECT

        # Internal events must have at least one occurrence to determine their year.
        year = self._get_enrolment_year()
        if year is None:
            return EnrolmentDeniedReason.EMPTY_EVENT

        # If the event belongs to an event group, group-level eligibility must pass.
        if self.event_group_id and (
            reason := self.event_group.get_enrolment_denied_reason(child)
        ):
            return reason

        # Check whether the child has reached the project's annual enrolment quota.
        if child.get_enrolment_count(year=year) >= child.project.enrolment_limit:
            return EnrolmentDeniedReason.YEARLY_ENROLMENT_LIMIT_REACHED

        # A child cannot enrol in the same internal event more than once.
        if self.id in child.get_enrolled_event_ids():
            return EnrolmentDeniedReason.ALREADY_JOINED_EVENT

        # A child cannot be assigned more than one password for the same external event.
        if self.id in child.get_ticket_system_passwords_by_event_id():
            return EnrolmentDeniedReason.ALREADY_HAS_PASSWORD_TO_EVENT

        return None

    def can_child_enroll(self, child: Child) -> bool:
        """Check if the child can enroll to the event."""
        return self.get_enrolment_denied_reason(child) is None

    @execute_in_background(thread_name="event-notification-sender", daemonic=False)
    def _send_event_notifications_to_guardians_in_background(self, *args, **kwargs):
        logger.info(
            "The sending of the event publishing notification "
            "will be executed in background!"
        )
        notification_service.send_event_notifications_to_guardians(*args, **kwargs)

    def publish(self, *, registration_opens_at, send_notifications=True):
        from events.services import validate_registration_opens_at

        validate_registration_opens_at(registration_opens_at)
        self._mark_published(registration_opens_at)

        if send_notifications:
            self._send_event_notifications_to_guardians_in_background(
                self,
                NotificationType.EVENT_PUBLISHED,
                list(self.project.children.prefetch_related("guardians")),
            )

    def _mark_published(self, registration_opens_at):
        """
        Mark the event published without validating the registration opening time
        or sending notifications.
        """
        with transaction.atomic():
            for occurrence in self.occurrences.all():
                occurrence.clean()

            self.published_at = timezone.now()
            self.registration_opens_at = registration_opens_at
            self.save()

            for occurrence in self.occurrences.all():
                occurrence.clean()
            logger.debug(
                "The atomic transaction to mark events published has now finished."
            )

    def is_published(self):
        return bool(self.published_at)

    def is_registration_open(self) -> bool:
        return (
            self.registration_opens_at is None
            or timezone.now() >= self.registration_opens_at
        )

    def _metric_children(self):
        return self.occurrences


class EventThemePath(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    theme_path = models.ForeignKey("tags.ThemePath", on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("event theme path")
        verbose_name_plural = _("event theme paths")
        constraints = [
            UniqueConstraint(
                fields=["event", "theme_path"], name="unique_event_theme_path"
            )
        ]

    def __str__(self):
        return f"{self.event} – {self.theme_path}"


class Occurrence(TimestampedModel, SerializableMixin):
    time = models.DateTimeField(verbose_name=_("time"))
    event = models.ForeignKey(
        Event,
        verbose_name=_("event"),
        related_name="occurrences",
        on_delete=models.CASCADE,
    )
    venue = models.ForeignKey(
        Venue,
        verbose_name=_("venue"),
        related_name="occurrences",
        on_delete=models.CASCADE,
    )

    children = models.ManyToManyField(
        Child,
        verbose_name=_("children"),
        related_name="occurrences",
        through="events.Enrolment",
        blank=True,
    )
    accessibilities = models.ManyToManyField(
        "tags.Accessibility",
        through="OccurrenceAccessibility",
        verbose_name=_("accessibilities"),
        related_name="occurrences",
        blank=True,
    )
    languages = models.ManyToManyField(
        "languages.Language",
        through="OccurrenceLanguage",
        verbose_name=_("languages"),
        related_name="occurrences",
        blank=True,
    )
    capacity_override = models.PositiveSmallIntegerField(
        verbose_name=_("capacity override"),
        null=True,
        blank=True,
        help_text=_(
            "Override total physical seat capacity. "
            "Each enrolment takes at least 2 seats "
            "(1 child + 1 guardian)."
        ),
    )
    attended_children_count_override = models.PositiveSmallIntegerField(
        verbose_name=_("attended children count override"),
        null=True,
        blank=True,
        help_text=_(
            "Override arrived children count for this occurrence. "
            "Must be set together with attended adults count override. "
            "When set, reports and Admin UI use the overrides instead of the sum "
            "of arrived enrolment participants."
        ),
    )
    attended_adults_count_override = models.PositiveSmallIntegerField(
        verbose_name=_("attended adults count override"),
        null=True,
        blank=True,
        help_text=_(
            "Override arrived adults count for this occurrence. "
            "Must be set together with attended children count override."
        ),
    )
    ticket_system_url = models.URLField(verbose_name=_("ticket system URL"), blank=True)

    serialize_fields = (
        {"name": "time", "accessor": lambda t: t.isoformat() if t else None},
        {"name": "event"},
        {"name": "venue"},
        {"name": "attended_children_count_override"},
        {"name": "attended_adults_count_override"},
    )

    objects = SerializableMixin.SerializableManager.from_queryset(OccurrenceQueryset)()

    class Meta:
        verbose_name = _("occurrence")
        verbose_name_plural = _("occurrences")
        constraints = [
            # The manual arrival override is a (children, adults) pair: both NULL
            # (no override) or both non-NULL, so the combined total is never
            # computed from a half-specified pair.
            _both_or_neither_constraint(
                "attended_children_count_override",
                "attended_adults_count_override",
                "occurrence_attended_overrides_both_or_neither",
            ),
        ]

    def __str__(self):
        return f"{self.time} ({self.pk})"

    def _clean_external_occurrence_count(self, event):
        if (
            event.is_external_ticket_system_event
            and event.pk
            and event.occurrences.exclude(pk=self.pk).exists()
        ):
            raise ValidationError(
                _("An external ticket system event can have at most one occurrence.")
            )

    def _clean_venue_system_compatibility(self, event):
        venue = getattr(self, "venue", None)
        if not venue or not getattr(self, "venue_id", None):
            return

        is_external = event.is_external_ticket_system_event
        if is_external != venue.is_system:
            msg = (
                _("External ticket system events must use the system venue.")
                if is_external
                else _("Internal events cannot use the system venue.")
            )
            raise ValidationError({"venue": msg})

    def _clean_ticket_system_url(self, event):
        if (
            event.published_at
            and event.is_external_ticket_system_event
            and not self.ticket_system_url
        ):
            raise ValidationError(
                _(
                    "Ticket system URL is required for all occurrences of a "
                    f"published {event.ticket_system} event."
                ),
                code=TICKET_SYSTEM_URL_MISSING_ERROR,
            )

    # Queryset annotation attribute names cached on `self.__dict__` by
    # OccurrenceQueryset (`with_remaining_capacity`, `with_attended_seats`,
    # `with_handled_enrolment_count`, `with_pending_arrival_seats`) and read first
    # by the corresponding `get_*` methods. These must be invalidated on `save()`
    # so updates to fields like `capacity_override` or `attended_count_override`
    # recalculate fresh values instead of returning stale pre-save annotations.
    _CACHED_ANNOTATION_ATTRS = (
        "reserved_seats",
        "remaining_capacity",
        "attended_seats",
        "attended_children_count",
        "attended_adults_count",
        "calculated_attended_seats",
        "handled_enrolment_count",
        "pending_arrival_seats",
        "enrolled_children_count",
        "enrolled_adults_count",
    )

    def _clean_attended_count_overrides_pair(self):
        """
        Validate that the children and adults arrival overrides are either both
        set or both empty.
        """
        if (self.attended_children_count_override is None) != (
            self.attended_adults_count_override is None
        ):
            raise ValidationError(
                {
                    "attended_children_count_override": _(
                        "Attended children and adults count overrides must both be "
                        "set or both be empty."
                    )
                }
            )

    def _clean_external_attended_count_override(self, event):
        """
        Validate that the attended count overrides are not set on occurrences of
        external ticket system events.
        """
        if event.is_external_ticket_system_event and (
            self.attended_children_count_override is not None
            or self.attended_adults_count_override is not None
        ):
            raise ValidationError(
                {
                    "attended_children_count_override": _(
                        "Cannot set attended count override on an external ticket "
                        "system event occurrence."
                    )
                }
            )

    def clean(self):
        super().clean()
        event = getattr(self, "event", None)
        if not event:
            return

        self._clean_external_occurrence_count(event)
        self._clean_venue_system_compatibility(event)
        self._clean_ticket_system_url(event)
        self._clean_external_attended_count_override(event)
        self._clean_attended_count_overrides_pair()

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)
        for attr in self._CACHED_ANNOTATION_ATTRS:
            self.__dict__.pop(attr, None)
        if not created:
            self.send_free_spot_notifications_if_needed()

    def delete(self, *args, **kwargs):
        if self.time > timezone.now():
            # this QS needs to be evaluated here, it would not work after the
            # occurrence has been deleted
            children = list(self.children.all())

            super().delete(*args, **kwargs)

            notification_service.send_event_notifications_to_guardians(
                self.event,
                NotificationType.OCCURRENCE_CANCELLED,
                children,
                occurrence=self,
            )
        else:
            super().delete(*args, **kwargs)

    def _get_annotated_or_compute(
        self,
        attr_name: str,
        fallback: Callable[[], int],
        *,
        external_zero: bool = False,
    ) -> int:
        if external_zero and self.event.is_external_ticket_system_event:
            return 0
        value = getattr(self, attr_name, _MISSING)
        if value is not _MISSING:
            return value
        return fallback()

    def _aggregate_enrolment_sum(self, expression, **filters) -> int:
        qs = self.enrolments.filter(**filters) if filters else self.enrolments
        return qs.aggregate(total=Coalesce(Sum(expression), Value(0)))["total"]

    def get_enrolment_count(self):
        return self._get_annotated_or_compute(
            "enrolment_count", lambda: self.enrolments.count()
        )

    def get_attended_enrolment_count(self):
        return self._get_annotated_or_compute(
            "attended_enrolment_count",
            lambda: self.enrolments.filter(attended=True).count(),
        )

    def get_handled_enrolment_count(self) -> int:
        """
        Return the number of enrolments whose attendance has been processed
        (`attended` is True or False, not NULL), or 0 for external events.
        """
        return self._get_annotated_or_compute(
            "handled_enrolment_count",
            lambda: self.enrolments.filter(attended__isnull=False).count(),
            external_zero=True,
        )

    def get_calculated_attended_seats(self) -> int:
        """
        Return the sum of arrived physical seats calculated across all enrolments
        of this occurrence, ignoring `attended_count_override` (0 for external events).
        """
        return self._get_annotated_or_compute(
            "calculated_attended_seats",
            lambda: self._aggregate_enrolment_sum(
                EnrolmentQueryset.arrived_seats_expression()
            ),
            external_zero=True,
        )

    def get_enrolled_children_count(self) -> int:
        return self._get_annotated_or_compute(
            "enrolled_children_count",
            lambda: self._aggregate_enrolment_sum(
                EnrolmentQueryset.children_expression()
            ),
        )

    def get_enrolled_adults_count(self) -> int:
        return self._get_annotated_or_compute(
            "enrolled_adults_count",
            lambda: self._aggregate_enrolment_sum(
                EnrolmentQueryset.adults_expression()
            ),
        )

    def _get_attended_participant_count(
        self, attr_name: str, override_attr: str, expression
    ) -> int:
        def fallback():
            if self.attended_count_override is not None:
                return getattr(self, override_attr)
            return self._aggregate_enrolment_sum(expression)

        return self._get_annotated_or_compute(attr_name, fallback, external_zero=True)

    def get_attended_children_count(self) -> int:
        return self._get_attended_participant_count(
            "attended_children_count",
            "attended_children_count_override",
            EnrolmentQueryset.arrived_children_expression(),
        )

    def get_attended_adults_count(self) -> int:
        return self._get_attended_participant_count(
            "attended_adults_count",
            "attended_adults_count_override",
            EnrolmentQueryset.arrived_adults_expression(),
        )

    def get_attended_seats(self) -> int:
        """
        Return the effective arrived physical seats for this occurrence:
        `attended_count_override` when set, otherwise `get_calculated_attended_seats()`
        (0 for external events).
        """

        def fallback():
            children = getattr(self, "attended_children_count", _MISSING)
            adults = getattr(self, "attended_adults_count", _MISSING)
            if children is not _MISSING and adults is not _MISSING:
                return children + adults
            if self.attended_count_override is not None:
                return self.attended_count_override
            return self.get_calculated_attended_seats()

        return self._get_annotated_or_compute(
            "attended_seats", fallback, external_zero=True
        )

    @property
    def attended_count_override(self) -> Optional[int]:
        """
        Return the combined manual arrival override (children + adults) when both
        override fields are set, otherwise None. Read-only: write the two
        underlying fields instead.
        """
        if (
            self.attended_children_count_override is None
            or self.attended_adults_count_override is None
        ):
            return None
        return (
            self.attended_children_count_override + self.attended_adults_count_override
        )

    @property
    def is_attended_count_overridden(self) -> bool:
        """
        Return True if this is an internal event occurrence with a manual
        arrival override (children + adults) set.
        """
        return (
            not self.event.is_external_ticket_system_event
            and self.attended_count_override is not None
        )

    def get_pending_arrival_seats(self) -> int:
        """
        Return the total booked physical seats of enrolments on this occurrence
        whose attendance has not yet been handled (`attended` is NULL), or 0 for
        external events.
        """
        return self._get_annotated_or_compute(
            "pending_arrival_seats",
            lambda: self._aggregate_enrolment_sum(
                EnrolmentQueryset.seats_expression(), attended__isnull=True
            ),
            external_zero=True,
        )

    def get_remaining_empty_seats(self) -> Optional[int]:
        """
        Return the number of physical seats currently unoccupied in this occurrence
        (`capacity - attended_seats`, floored at 0), or None if capacity is unset.
        """
        if self.event.is_external_ticket_system_event:
            return 0
        capacity = self.get_capacity()
        if capacity is None:
            return None
        return max(capacity - self.get_attended_seats(), 0)

    def get_free_spot_notification_subscription_count(self):
        return self._get_annotated_or_compute(
            "free_spot_notification_subscription_count",
            lambda: self.free_spot_notification_subscriptions.count(),
        )

    def get_capacity(self) -> Optional[int]:
        if self.event.is_external_ticket_system_event:
            return 0
        if self.capacity_override is not None:
            return self.capacity_override
        else:
            return self.event.capacity_per_occurrence

    def get_reserved_seats(self) -> int:
        def fallback():
            children = getattr(self, "enrolled_children_count", _MISSING)
            adults = getattr(self, "enrolled_adults_count", _MISSING)
            if children is not _MISSING and adults is not _MISSING:
                return children + adults
            return self._aggregate_enrolment_sum(EnrolmentQueryset.seats_expression())

        return self._get_annotated_or_compute("reserved_seats", fallback)

    def get_remaining_capacity(self) -> int:
        return self._get_annotated_or_compute(
            "remaining_capacity",
            lambda: max((self.get_capacity() or 0) - self.get_reserved_seats(), 0),
        )

    def has_free_seats(self, requested_seats: int = MIN_SEATS_PER_ENROLMENT) -> bool:
        return self.get_remaining_capacity() >= requested_seats

    def get_enrolment_denied_reason(
        self, child: Child, requested_seats: int = MIN_SEATS_PER_ENROLMENT
    ) -> None | EnrolmentDeniedReason:
        """
        Why, if for any reason, the given child can't enrol to this occurrence?

        :return: None if the child can enrol, otherwise the reason why not.
        """
        if reason := self.event.get_enrolment_denied_reason(child):
            return reason

        if not self.has_free_seats(requested_seats):
            return EnrolmentDeniedReason.OCCURRENCE_FULL

        if self.time < timezone.now():
            return EnrolmentDeniedReason.PAST_OCCURRENCE

        if (
            child.get_enrolment_count(year=year_of(self.time))
            >= self.event.project.enrolment_limit
        ):
            return EnrolmentDeniedReason.YEARLY_ENROLMENT_LIMIT_REACHED

        return None

    def can_child_enroll(self, child: Child) -> bool:
        """Check if the child can enroll to this occurrence."""
        return self.get_enrolment_denied_reason(child) is None

    def can_user_administer(
        self, user, user_organisation_ids: Optional[set] = None
    ) -> bool:
        # There shouldn't ever be a situation where event.project != venue.project
        # so we can just check one of them
        return self.event.can_user_administer(
            user, user_organisation_ids=user_organisation_ids
        )

    def send_free_spot_notifications_if_needed(self):
        if (
            self.has_free_seats()
            # Normally the event shouldn't be unpublished or in the past ever when
            # coming here. These checks are just for making sure no notifications are
            # sent in possible abnormal situations either for those events.
            and self.event.is_published()
            and timezone.now() < self.time
        ):
            self.free_spot_notification_subscriptions.send_notification()


class OccurrenceAccessibility(models.Model):
    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE)
    accessibility = models.ForeignKey("tags.Accessibility", on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("occurrence accessibility")
        verbose_name_plural = _("occurrence accessibilities")
        constraints = [
            UniqueConstraint(
                fields=["occurrence", "accessibility"],
                name="unique_occurrence_accessibility",
            )
        ]

    def __str__(self):
        return f"{self.occurrence} – {self.accessibility}"


class OccurrenceLanguage(models.Model):
    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE)
    language = models.ForeignKey("languages.Language", on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("occurrence language")
        verbose_name_plural = _("occurrence languages")
        constraints = [
            UniqueConstraint(
                fields=["occurrence", "language"],
                name="unique_occurrence_language",
            )
        ]

    def __str__(self):
        return f"{self.occurrence} – {self.language}"


class Enrolment(TimestampedModel, SerializableMixin):
    child = models.ForeignKey(
        Child,
        related_name="enrolments",
        on_delete=models.SET_NULL,
        verbose_name=_("child"),
        null=True,
        blank=True,
    )
    occurrence = models.ForeignKey(
        Occurrence,
        related_name="enrolments",
        on_delete=models.CASCADE,
        verbose_name=_("occurrence"),
    )
    attended = models.BooleanField(verbose_name=_("attended"), null=True, blank=True)
    arrived_children_count = models.PositiveSmallIntegerField(
        verbose_name=_("arrived children count"),
        null=True,
        blank=True,
    )
    arrived_guardians_count = models.PositiveSmallIntegerField(
        verbose_name=_("arrived guardians count"),
        null=True,
        blank=True,
    )
    extra_children_count = models.PositiveSmallIntegerField(
        verbose_name=_("extra children count"),
        null=True,
        blank=True,
        help_text=_(
            "Additional children beyond the enrolled child (empty/NULL means 0)."
        ),
    )
    extra_guardians_count = models.PositiveSmallIntegerField(
        verbose_name=_("extra guardians count"),
        null=True,
        blank=True,
        help_text=_(
            "Additional adults/guardians beyond the accompanying adult "
            "(empty/NULL means 0)."
        ),
    )
    reminder_sent_at = models.DateTimeField(
        verbose_name=_("reminder sent at"), null=True, blank=True
    )
    feedback_notification_sent_at = models.DateTimeField(
        verbose_name=_("feedback notification sent at"), null=True, blank=True
    )

    serialize_fields = (
        {"name": "child", "accessor": lambda c: str(c)},
        {"name": "occurrence"},
        {"name": "extra_children_count"},
        {"name": "extra_guardians_count"},
        {"name": "arrived_children_count"},
        {"name": "arrived_guardians_count"},
    )

    objects = SerializableMixin.SerializableManager.from_queryset(EnrolmentQueryset)()

    class Meta:
        verbose_name = _("enrolment")
        verbose_name_plural = _("enrolments")
        constraints = [
            models.UniqueConstraint(
                fields=["child", "occurrence"], name="unq_child_occurrence"
            ),
            # Extra participant counts must be recorded as a pair (both NULL when not
            # used, or both non-NULL integers) so seat calculations and admin/API state
            # never see a half-specified extra participant pair.
            _both_or_neither_constraint(
                "extra_children_count",
                "extra_guardians_count",
                "enrolment_extra_counts_both_or_neither",
            ),
            # Arrived participant counts must also be recorded as a pair: either both
            # NULL (when attendance has not been handled yet, or on legacy rows that
            # only recorded the boolean `attended` flag) or both non-NULL integers.
            # This prevents half-populated arrival state and guarantees SQL addition
            # (`arrived_children_count + arrived_guardians_count`) never yields NULL
            # due to a single missing column.
            _both_or_neither_constraint(
                "arrived_children_count",
                "arrived_guardians_count",
                "enrolment_arrived_counts_both_or_neither",
            ),
        ]
        ordering = ("id",)

    @property
    def total_seats(self) -> int:
        """
        Return the total number of physical seats reserved by this enrolment
        (1 default child + 1 default guardian + any extra children and guardians).
        """
        return (
            MIN_SEATS_PER_ENROLMENT
            + (self.extra_children_count or 0)
            + (self.extra_guardians_count or 0)
        )

    @property
    def booked_children_count(self) -> int:
        """
        Return the total number of children booked on this enrolment
        (1 enrolled child + `extra_children_count`).
        """
        return 1 + (self.extra_children_count or 0)

    @property
    def booked_guardians_count(self) -> int:
        """
        Return the total number of adults/guardians booked on this enrolment
        (1 accompanying guardian + `extra_guardians_count`).
        """
        return 1 + (self.extra_guardians_count or 0)

    @property
    def arrived_seats(self) -> int:
        """
        Return the number of arrived physical seats for this enrolment:
        `arrived_children_count + arrived_guardians_count` when recorded, falling
        back to `total_seats` when `attended=True` without explicit counts, or 0.
        """
        if (
            self.arrived_children_count is not None
            and self.arrived_guardians_count is not None
        ):
            return self.arrived_children_count + self.arrived_guardians_count
        if self.attended is True:
            return self.total_seats
        return 0

    def clean(self):
        super().clean()
        children = self.arrived_children_count
        guardians = self.arrived_guardians_count
        if (children is None) != (guardians is None):
            raise ValidationError(
                _(
                    "Arrived children count and arrived guardians count must both be "
                    "set or both be empty."
                )
            )
        if children is not None and guardians is not None:
            if children > self.booked_children_count:
                raise ValidationError(
                    {
                        "arrived_children_count": _(
                            "Arrived children count cannot exceed "
                            "booked children count."
                        )
                    }
                )
            if guardians > self.booked_guardians_count:
                raise ValidationError(
                    {
                        "arrived_guardians_count": _(
                            "Arrived guardians count cannot exceed "
                            "booked guardians count."
                        )
                    }
                )
            expected_attended = (children + guardians) > 0
            if self.attended is not expected_attended:
                raise ValidationError(
                    {
                        "attended": _(
                            "Attended status must match whether any arrived "
                            "participants were recorded."
                        )
                    }
                )

    def __str__(self):
        return f"{self.pk} {self.child_id}"

    def save(self, *args, **kwargs):
        created = self.pk is None

        with transaction.atomic():
            super().save(*args, **kwargs)

            if created:
                event_group = self.occurrence.event.event_group
                events = (
                    event_group.events.all() if event_group else [self.occurrence.event]
                )
                self.child.free_spot_notification_subscriptions.filter(
                    occurrence__event__in=events
                ).delete()

        if created:
            notification_service.send_enrolment_creation_notification(self)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.occurrence.send_free_spot_notifications_if_needed()

    def delete_and_send_notification(self):
        child = self.child
        occurrence = self.occurrence
        self.delete()

        notification_service.send_event_notifications_to_guardians(
            occurrence.event,
            NotificationType.OCCURRENCE_UNENROLMENT,
            child,
            occurrence=occurrence,
        )

    def can_user_administer(self, user):
        return self.occurrence.can_user_administer(user)

    @transaction.atomic()
    def send_reminder_notification(self, force=False):
        if self.reminder_sent_at and not force:
            logger.warning(
                f"Tried to send already sent reminder notification for enrolment {self}"
            )
            return

        # an additional instance level sanity check to prevent sending reminder
        # notifications related to occurrences already in the past
        if self.occurrence.time < timezone.now() and not force:
            logger.warning(
                f"Tried to send reminder notification related to an occurrence already "
                f"in the past, enrolment: {self}"
            )
            return

        self.reminder_sent_at = timezone.now()
        self.save()
        notification_service.send_event_reminder_notification(self)

    @transaction.atomic()
    def send_feedback_notification(self, force=False):
        if self.feedback_notification_sent_at and not force:
            logger.warning(
                f"Tried to send already sent feedback notification for enrolment {self}"
            )
            return

        # an additional instance level sanity check to prevent sending feedback
        # notifications related to too old enrolments
        if self.occurrence.time < (timezone.now() - timedelta(days=7)) and not force:
            logger.warning(
                f"Tried to send feedback notification of too old occurrence, "
                f"enrolment: {self}"
            )
            return

        self.feedback_notification_sent_at = timezone.now()
        self.save()

        notification_service.send_event_notifications_to_guardians(
            self.occurrence.event,
            NotificationType.OCCURRENCE_FEEDBACK,
            self.child,
            occurrence=self.occurrence,
            enrolment=self,
        )

    def is_upcoming(self):
        return self.occurrence.time >= timezone.now()

    @property
    def reference_id(self):
        """The enrolment id encoded with Kukkuu hashids utils."""
        hashids = get_hashid_service()
        return hashids.encode(self.id)

    @classmethod
    def decode_reference_id(cls, reference_id: str) -> Optional[int]:
        """Decode the enrolment reference id
        which is encoded with Kukkuu hashids utils."""
        hashids = get_hashid_service()
        enrolment_id = hashids.decode(reference_id)
        if not enrolment_id:
            raise IllegalEnrolmentReferenceId("Could not decode the enrolment id")
        return enrolment_id[0]


class TicketSystemPassword(SerializableMixin, models.Model):
    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    assigned_at = models.DateTimeField(
        verbose_name=_("assigned at"), blank=True, null=True
    )
    value = models.CharField(max_length=64, verbose_name=_("value"))
    event = models.ForeignKey(
        Event,
        verbose_name=_("event"),
        related_name="ticket_system_passwords",
        on_delete=models.CASCADE,
    )
    child = models.ForeignKey(
        Child,
        verbose_name=_("child"),
        related_name="ticket_system_passwords",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    serialize_fields = [
        {"name": "assigned_at", "accessor": lambda t: t.isoformat() if t else None},
        {"name": "value"},
        {"name": "event"},
        {"name": "child", "accessor": lambda c: str(c)},
    ]

    objects = SerializableMixin.SerializableManager.from_queryset(
        TicketSystemPasswordQueryset
    )()

    class Meta:
        verbose_name = _("ticket system password")
        verbose_name_plural = _("ticket system passwords")
        ordering = ("id",)
        constraints = (
            UniqueConstraint(
                fields=["value", "event"], name="unique_password_value_event"
            ),
            UniqueConstraint(
                fields=["event", "child"], name="unique_password_event_child"
            ),
        )

    def assign(self, child: Child) -> None:
        if self.child:
            raise PasswordAlreadyAssignedError("The password is already assigned.")

        if TicketSystemPassword.objects.filter(event=self.event, child=child).exists():
            raise PasswordAlreadyAssignedError(
                "A password is already assigned to the given child/event pair."
            )

        self.assigned_at = timezone.now()
        self.child = child
        self.save()

        logger.info(
            f'Ticket system password "{self.value}" assigned to {child.pk} to '
            f"{self.event}"
        )
