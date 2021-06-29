from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F, Q
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatedFields

from children.models import Child
from common.models import TimestampedModel, TranslatableModel, TranslatableQuerySet
from events.consts import NotificationType
from events.utils import (
    send_event_group_notifications_to_guardians,
    send_event_notifications_to_guardians,
)
from kukkuu.consts import EVENT_GROUP_NOT_READY_FOR_PUBLISHING_ERROR
from venues.models import Venue


class EventGroupQueryset(TranslatableQuerySet):
    def user_can_view(self, user):
        return self.filter(
            Q(project__in=user.administered_projects) | Q(published_at__isnull=False)
        ).distinct()


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

    def publish(self):
        unpublished_events = self.events.unpublished()
        if any(not e.ready_for_event_group_publishing for e in unpublished_events):
            raise ValidationError(
                f"All events are not ready for event group publishing.",
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

    def available(self, child):
        """
        A child's available events must match all of the following rules:
            * the event must be published
            * the event must have at least one occurrence in the future
            * the child must not have enrolled to the event
            * the child must not have enrolled to any event in the same event group
              as the event
        """
        child_enrolled_event_groups = EventGroup.objects.filter(
            events__occurrences__in=child.occurrences.all()
        )
        return (
            self.published()
            .filter(occurrences__time__gte=timezone.now())
            .distinct()
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
        verbose_name=_("capacity per occurrence")
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
            and self.capacity_per_occurrence > old_capacity_per_occurrence
        ):
            self.occurrences.send_free_spot_notifications_if_needed()

    def can_user_administer(self, user):
        return user.can_administer_project(self.project)

    def can_user_publish(self, user):
        return user.can_publish_in_project(self.project)

    @transaction.atomic
    def publish(self, send_notifications=True):
        self.published_at = timezone.now()
        self.save()

        if send_notifications:
            send_event_notifications_to_guardians(
                self,
                NotificationType.EVENT_PUBLISHED,
                self.project.children.prefetch_related("guardians"),
            )

    def is_published(self):
        return bool(self.published_at)


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
        return self.filter(time__gt=now())

    def in_past(self):
        return self.exclude(time__gt=now())


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

    objects = OccurrenceQueryset.as_manager()

    class Meta:
        verbose_name = _("occurrence")
        verbose_name_plural = _("occurrences")

    def __str__(self):
        return f"{self.time} ({self.pk})"

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)
        if not created:
            self.send_free_spot_notifications_if_needed()

    def delete(self, *args, **kwargs):
        if self.time >= now():
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
        return self.filter(occurrence__time__gt=now())

    def send_reminder_notifications(self):
        today = timezone.localtime().date()
        close_enough = today + timedelta(days=settings.KUKKUU_REMINDER_DAYS_IN_ADVANCE)
        tomorrow = today + timedelta(days=1)

        count = 0
        for enrolment in self.filter(
            reminder_sent_at=None,
            created_at__date__lt=F("occurrence__time__date")
            - timedelta(days=settings.KUKKUU_REMINDER_DAYS_IN_ADVANCE),
            occurrence__time__date__lte=close_enough,
            occurrence__time__date__gte=tomorrow,
            child__guardians__isnull=False,
        ):
            enrolment.send_reminder_notification()
            count += 1

        return count


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
    attended = models.NullBooleanField(verbose_name=_("attended"))
    reminder_sent_at = models.DateTimeField(
        verbose_name=_("reminder sent at"), null=True, blank=True
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

    def __str__(self):
        return f"{self.pk} {self.child_id}"

    def save(self, *args, **kwargs):
        created = self.pk is None

        with transaction.atomic():
            super().save(*args, **kwargs)

            if created:
                self.child.free_spot_notification_subscriptions.filter(
                    occurrence__event=self.occurrence.event
                ).delete()

        if created:
            send_event_notifications_to_guardians(
                self.occurrence.event,
                NotificationType.OCCURRENCE_ENROLMENT,
                self.child,
                occurrence=self.occurrence,
            )

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

    def send_reminder_notification(self):
        self.reminder_sent_at = timezone.now()
        self.save()

        send_event_notifications_to_guardians(
            self.occurrence.event,
            NotificationType.OCCURRENCE_REMINDER,
            self.child,
            occurrence=self.occurrence,
            enrolment=self,
        )

    def is_upcoming(self):
        return self.occurrence.time >= timezone.now()
