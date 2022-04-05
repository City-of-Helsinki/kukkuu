import logging
import warnings
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import ExpressionWrapper, F, Q, UniqueConstraint
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatedFields

import events.notification_service as notification_service
from children.models import Child
from common.models import TimestampedModel, TranslatableModel, TranslatableQuerySet
from events.consts import NotificationType
from events.utils import (
    send_event_group_notifications_to_guardians,
    send_event_notifications_to_guardians,
)
from kukkuu.consts import (
    DATA_VALIDATION_ERROR,
    EVENT_GROUP_NOT_READY_FOR_PUBLISHING_ERROR,
    TICKET_SYSTEM_URL_MISSING_ERROR,
)
from kukkuu.exceptions import IllegalEnrolmentReferenceId
from kukkuu.service import get_hashid_service
from venues.models import Venue

logger = logging.getLogger(__name__)


class EventGroupQueryset(TranslatableQuerySet):
    def user_can_view(self, user):
        return self.filter(
            Q(project__in=user.administered_projects) | Q(published_at__isnull=False)
        ).distinct()

    def published(self):
        return self.filter(published_at__isnull=False)

    def upcoming(self):
        return self.filter(events__occurrences__time__gte=timezone.now()).distinct()


class EventGroup(TimestampedModel, TranslatableModel):
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

    objects = EventGroupQueryset.as_manager()

    class Meta:
        verbose_name = _("event group")
        verbose_name_plural = _("event groups")
        ordering = ("id",)

    def __str__(self):
        name = self.safe_translation_getter("name", super().__str__())
        published_text = _("published") if self.published_at else _("unpublished")
        return f"{name} ({self.pk}) ({self.project.year}) ({published_text})"

    def can_user_administer(self, user):
        return user.can_administer_project(self.project)

    def can_user_publish(self, user):
        return user.can_publish_in_project(self.project)

    def can_child_enroll(self, child) -> bool:
        """Check if the child can enroll to an event in the event group."""

        if occurrence := Occurrence.objects.filter(event__event_group=self).first():
            # Need to have at least one occurrence
            year = occurrence.time.year
        else:
            return False

        if (
            child.occurrences.filter(time__year=year).count()
            >= child.project.enrolment_limit
        ):
            return False

        if child.occurrences.filter(event__event_group=self).exists():
            return False

        return True

    def publish(self):
        unpublished_events = self.events.unpublished()
        if any(not e.ready_for_event_group_publishing for e in unpublished_events):
            raise ValidationError(
                "All events are not ready for event group publishing.",
                code=EVENT_GROUP_NOT_READY_FOR_PUBLISHING_ERROR,
            )

        with transaction.atomic():
            self.published_at = timezone.now()
            self.save()

            for event in unpublished_events:
                event.publish(send_notifications=False)

            send_event_group_notifications_to_guardians(
                self,
                NotificationType.EVENT_GROUP_PUBLISHED,
                self.project.children.prefetch_related("guardians"),
            )

    def is_published(self):
        return bool(self.published_at)


# This need to be inherited from TranslatableQuerySet instead of default model.QuerySet
class EventQueryset(TranslatableQuerySet):
    def user_can_view(self, user):
        return self.filter(
            Q(project__in=user.administered_projects) | Q(published_at__isnull=False)
        ).distinct()

    def published(self):
        return self.filter(published_at__isnull=False)

    def unpublished(self):
        return self.filter(published_at__isnull=True)

    def upcoming(self):
        return self.filter(occurrences__time__gte=timezone.now()).distinct()

    def available(self, child):
        """
        A child's available events must match all of the following rules:
            * the event must be published
            * the event must have at least one occurrence in the future
            * the child must not have enrolled to the event
            * the child must not have enrolled to any event in the same event group
              as the event
        """

        warnings.warn(
            "Query doesn't exclude events when yearly "
            "limit of enrolments have been exceeded.",
            DeprecationWarning,
            stacklevel=2,
        )

        child_enrolled_event_groups = EventGroup.objects.filter(
            events__occurrences__in=child.occurrences.all()
        )
        return (
            self.published()
            .upcoming()
            .exclude(occurrences__in=child.occurrences.all())
            .exclude(event_group__in=child_enrolled_event_groups)
        )


class Event(TimestampedModel, TranslatableModel):
    CHILD_AND_GUARDIAN = "child_and_guardian"
    CHILD_AND_1_OR_2_GUARDIANS = "child_and_1_or_2_guardians"
    FAMILY = "family"
    PARTICIPANTS_PER_INVITE_CHOICES = (
        (CHILD_AND_GUARDIAN, _("Child and guardian")),
        (CHILD_AND_1_OR_2_GUARDIANS, _("Child and 1-2 guardians")),
        (FAMILY, _("Family")),
    )

    INTERNAL = "internal"
    TICKETMASTER = "ticketmaster"
    TICKET_SYSTEM_CHOICES = (
        (INTERNAL, _("Internal")),
        (TICKETMASTER, _("Ticketmaster")),
    )

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
        verbose_name=_("capacity per occurrence"), null=True, blank=True
    )
    published_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("published at")
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

    objects = EventQueryset.as_manager()

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")

    def __str__(self):
        name = self.safe_translation_getter("name", super().__str__())
        published_text = _("published") if self.published_at else _("unpublished")
        return f"{name} ({self.pk}) ({self.project.year}) ({published_text})"

    def clean(self):
        if (
            self.ticket_system == Event.INTERNAL
            and self.capacity_per_occurrence is None
        ):
            raise ValidationError(
                _(
                    "Capacity per occurrence is required when ticket system is "
                    "internal."
                ),
                code=DATA_VALIDATION_ERROR,
            )

    def save(self, *args, **kwargs):
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

    def can_user_administer(self, user):
        return user.can_administer_project(self.project)

    def can_user_publish(self, user):
        return user.can_publish_in_project(self.project)

    def can_child_enroll(self, child: Child) -> bool:
        """Check if the child can enroll to the event."""

        if occurrence := self.occurrences.first():
            # Need to have at least one occurrence
            year = occurrence.time.year
        else:
            return False

        if self.event_group and not self.event_group.can_child_enroll(child):
            return False

        if (
            child.occurrences.filter(time__year=year).count()
            >= child.project.enrolment_limit
        ):
            return False

        if child.occurrences.filter(event=self).exists():
            return False

        return True

    @transaction.atomic
    def publish(self, send_notifications=True):
        for occurrence in self.occurrences.all():
            occurrence.clean()

        self.published_at = timezone.now()
        self.save()

        for occurrence in self.occurrences.all():
            occurrence.clean()

        if send_notifications:
            send_event_notifications_to_guardians(
                self,
                NotificationType.EVENT_PUBLISHED,
                self.project.children.prefetch_related("guardians"),
            )

    def is_published(self):
        return bool(self.published_at)

    def get_or_assign_ticket_system_password(self, child):
        try:
            return self.ticket_system_passwords.get(child=child).value
        except TicketSystemPassword.DoesNotExist:
            return TicketSystemPassword.objects.assign(self, child).value


class OccurrenceQueryset(models.QuerySet):
    def user_can_view(self, user):
        return self.filter(
            Q(event__project__in=user.administered_projects)
            | Q(event__published_at__isnull=False)
        ).distinct()

    def delete(self, *args, **kwargs):
        for obj in self:
            obj.delete()

    def send_free_spot_notifications_if_needed(self):
        for obj in self:
            obj.send_free_spot_notifications_if_needed()

    def upcoming(self):
        return self.filter(time__gte=timezone.now())

    def upcoming_with_leeway(self):
        return self.filter(
            time__gte=timezone.now()
            - timedelta(minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY)
        )

    def upcoming_with_ongoing(self):
        """Return occurrences that are upcoming or still ongoing (with added leeway)."""
        qs = self.with_end_time()
        return qs.filter(
            end_time__gte=timezone.now()
            - timedelta(minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY)
        )

    def in_past(self):
        return self.exclude(time__gt=timezone.now())

    def with_end_time(self):
        return self.annotate(
            end_time=ExpressionWrapper(
                F("time")
                + Coalesce(
                    F("event__duration"),
                    settings.KUKKUU_DEFAULT_EVENT_DURATION,
                )
                * timedelta(minutes=1),
                output_field=models.DateTimeField(),
            ),
        )


class Occurrence(TimestampedModel):
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
    occurrence_language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        verbose_name=_("occurrence language"),
        default=settings.LANGUAGES[0][0],
    )
    capacity_override = models.PositiveSmallIntegerField(
        verbose_name=_("capacity override"),
        null=True,
        blank=True,
        help_text=_(
            "When set will be used as the capacity of this occurrence instead of "
            "the value coming from the event."
        ),
    )
    ticket_system_url = models.URLField(verbose_name=_("ticket system URL"), blank=True)

    objects = OccurrenceQueryset.as_manager()

    class Meta:
        verbose_name = _("occurrence")
        verbose_name_plural = _("occurrences")

    def __str__(self):
        return f"{self.time} ({self.pk})"

    def clean(self):
        if (
            self.event.published_at
            and self.event.ticket_system == Event.TICKETMASTER
            and not self.ticket_system_url
        ):
            raise ValidationError(
                _(
                    "Ticket system URL is required for all occurrences of a "
                    "published Ticketmaster event."
                ),
                code=TICKET_SYSTEM_URL_MISSING_ERROR,
            )

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)
        if not created:
            self.send_free_spot_notifications_if_needed()

    def delete(self, *args, **kwargs):
        if self.time > timezone.now():
            # this QS needs to be evaluated here, it would not work after the
            # occurrence has been deleted
            children = list(self.children.all())

            super().delete(*args, **kwargs)

            send_event_notifications_to_guardians(
                self.event,
                NotificationType.OCCURRENCE_CANCELLED,
                children,
                occurrence=self,
            )
        else:
            super().delete(*args, **kwargs)

    def get_enrolment_count(self):
        try:
            # try to use an annotated value
            return self.enrolment_count
        except AttributeError:
            return self.enrolments.count()

    def get_capacity(self):
        if self.capacity_override is not None:
            return self.capacity_override
        else:
            return self.event.capacity_per_occurrence

    def get_remaining_capacity(self):
        return max(self.get_capacity() - self.get_enrolment_count(), 0)

    def can_user_administer(self, user):
        # There shouldn't ever be a situation where event.project != venue.project
        # so we can just check one of them
        return self.event.can_user_administer(user)

    def send_free_spot_notifications_if_needed(self):
        if (
            self.get_remaining_capacity()
            # Normally the event shouldn't be unpublished or in the past ever when
            # coming here. These checks are just for making sure no notifications are
            # sent in possible abnormal situations either for those events.
            and self.event.is_published()
            and timezone.now() < self.time
        ):
            self.free_spot_notification_subscriptions.send_notification()


class EnrolmentQueryset(models.QuerySet):
    def user_can_view(self, user):
        return self.filter(
            Q(child__guardians__user=user)
            | Q(child__project__in=user.administered_projects)
        ).distinct()

    @transaction.atomic()
    def delete(self):
        for enrolment in self:
            enrolment.delete()

    def upcoming(self):
        return self.filter(occurrence__time__gte=timezone.now())

    def with_end_time(self):
        return self.annotate(
            end_time=ExpressionWrapper(
                F("occurrence__time")
                + Coalesce(
                    F("occurrence__event__duration"),
                    settings.KUKKUU_DEFAULT_EVENT_DURATION,
                )
                * timedelta(minutes=1),
                output_field=models.DateTimeField(),
            ),
        )

    def send_reminder_notifications(self):
        today = timezone.localtime().date()
        close_enough = today + timedelta(days=settings.KUKKUU_REMINDER_DAYS_IN_ADVANCE)
        tomorrow = today + timedelta(days=1)

        enrolments = self.filter(
            reminder_sent_at=None,
            created_at__date__lt=F("occurrence__time__date")
            - timedelta(days=settings.KUKKUU_REMINDER_DAYS_IN_ADVANCE),
            occurrence__time__date__lte=close_enough,
            occurrence__time__date__gte=tomorrow,
            child__guardians__isnull=False,
        ).select_related("occurrence")
        for enrolment in enrolments:
            enrolment.send_reminder_notification()

        return len(enrolments)

    def send_feedback_notifications(self):
        now = timezone.now()
        delay = timedelta(minutes=settings.KUKKUU_FEEDBACK_NOTIFICATION_DELAY)

        enrolments = (
            self.with_end_time()
            .filter(
                feedback_notification_sent_at=None,
                child__guardians__isnull=False,
                end_time__lte=now - delay,
                # we never want to send feedback notifications related to occurrences
                # that took place over a week ago
                occurrence__time__range=(now - timedelta(days=7), now),
            )
            .select_related("occurrence")
        )
        for enrolment in enrolments:
            enrolment.send_feedback_notification()

        return len(enrolments)


class Enrolment(TimestampedModel):
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
    reminder_sent_at = models.DateTimeField(
        verbose_name=_("reminder sent at"), null=True, blank=True
    )
    feedback_notification_sent_at = models.DateTimeField(
        verbose_name=_("feedback notification sent at"), null=True, blank=True
    )

    objects = EnrolmentQueryset.as_manager()

    class Meta:
        verbose_name = _("enrolment")
        verbose_name_plural = _("enrolments")
        constraints = [
            models.UniqueConstraint(
                fields=["child", "occurrence"], name="unq_child_occurrence"
            )
        ]
        ordering = ("id",)

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

        send_event_notifications_to_guardians(
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

        send_event_notifications_to_guardians(
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


class NoFreePasswordsError(Exception):
    pass


class PasswordAlreadyAssignedError(Exception):
    pass


class TicketSystemPasswordQueryset(models.QuerySet):
    def free(self):
        return self.filter(child=None)

    @transaction.atomic
    def assign(self, event, child):
        obj = (
            self.select_for_update(skip_locked=True).filter(event=event).free().first()
        )
        if not obj:
            logger.error(
                f"No free ticket system passwords left to event {event}, "
                f"one was requested for child {child.pk}."
            )
            raise NoFreePasswordsError(
                f"No free ticket system passwords left to event {event}."
            )

        obj.assign(event, child)

        return obj


class TicketSystemPassword(models.Model):
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

    objects = TicketSystemPasswordQueryset.as_manager()

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

    def assign(self, event, child):
        if self.child:
            raise PasswordAlreadyAssignedError("The password is already assigned.")

        self.assigned_at = timezone.now()
        self.child = child
        self.save()

        logger.info(
            f'Ticket system password "{self.value}" assigned to {child.pk} to {event}.'
        )
