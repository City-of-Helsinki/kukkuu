from django.db import models
from django.db.models import Count, Exists, F, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatedFields

import messaging.service as messaging_service
from children.models import Child
from common.models import TimestampedModel, TranslatableModel, TranslatableQuerySet
from events.models import Enrolment, Event, EventGroup, Occurrence
from projects.models import Project
from subscriptions.models import FreeSpotNotificationSubscription
from users.models import Guardian


class MessageQuerySet(TranslatableQuerySet):
    def user_can_view(self, user):
        return self.filter(project__in=user.administered_projects)


class Message(TimestampedModel, TranslatableModel):
    ALL = "all"
    INVITED = "invited"
    ENROLLED = "enrolled"
    ATTENDED = "attended"
    SUBSCRIBED_TO_FREE_SPOT_NOTIFICATION = "subscribed_to_free_spot_notification"
    RECIPIENT_SELECTION_CHOICES = (
        (ALL, _("All")),
        (INVITED, _("Invited")),
        (ENROLLED, _("Enrolled")),
        (ATTENDED, _("Attended")),
        (
            SUBSCRIBED_TO_FREE_SPOT_NOTIFICATION,
            _("Subscribed to free spot notification"),
        ),
    )
    EMAIL = "email"
    SMS = "sms"
    PROTOCOL_CHOICES = ((EMAIL, _("Email")), (SMS, _("SMS")))
    protocol = models.CharField(
        max_length=16,
        verbose_name=_("notification type"),
        choices=PROTOCOL_CHOICES,
        default=EMAIL,
    )
    project = models.ForeignKey(
        Project,
        verbose_name=_("project"),
        related_name="messages",
        on_delete=models.CASCADE,
    )
    translations = TranslatedFields(
        subject=models.CharField(verbose_name=_("subject"), max_length=255),
        body_text=models.TextField(verbose_name=_("body plain text")),
    )
    sent_at = models.DateTimeField(verbose_name=_("sent at"), blank=True, null=True)
    recipient_count = models.PositiveIntegerField(
        verbose_name=_("recipient count"), blank=True, null=True
    )
    recipient_selection = models.CharField(
        max_length=64,
        verbose_name=_("recipient selection"),
        choices=RECIPIENT_SELECTION_CHOICES,
    )
    event = models.ForeignKey(
        Event,
        verbose_name=_("event"),
        related_name="messages",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    occurrences = models.ManyToManyField(
        Occurrence,
        verbose_name=_("occurrences"),
        related_name="messages",
        blank=True,
    )

    objects = MessageQuerySet.as_manager()

    class Meta:
        ordering = ("id",)
        verbose_name = _("message")
        verbose_name_plural = _("messages")

    def __str__(self):
        return f"({self.pk}) {self.subject} ({self.sent_at or 'not sent'})"

    def get_recipient_count(self):
        return (
            self.recipient_count
            if self.sent_at
            else self.get_recipient_guardians().count()
        )

    def send(self, *, force=False):
        messaging_service.send_message(self, force=force)

    def get_recipient_guardians(self):
        guardians = Guardian.objects.filter(children__project=self.project)

        if self.recipient_selection == Message.ALL:
            return guardians.distinct()

        now = timezone.now()
        children = Child.objects.filter(project=self.project, guardians__isnull=False)
        enrolments = Enrolment.objects.filter(child__in=children)
        subscriptions = FreeSpotNotificationSubscription.objects.filter(
            child__in=children
        )

        if self.occurrences.exists():
            occurrences = self.occurrences.all()
            enrolments = enrolments.filter(occurrence__in=occurrences)
            subscriptions = subscriptions.filter(occurrence__in=occurrences)
        elif self.event_id:
            occurrences = self.event.occurrences.all()
            enrolments = enrolments.filter(occurrence__in=occurrences)
            subscriptions = subscriptions.filter(occurrence__in=occurrences)

        if self.recipient_selection == Message.INVITED:
            # There is an upcoming event for which the user hasn't enrolled
            # in. For event groups this additionally means that user shouldn't be
            # enrolled in any other events belonging to the same event group.
            upcoming_events = Event.objects.filter(
                project=self.project, occurrences__time__gte=now
            ).published()

            upcoming_single_events = upcoming_events.filter(event_group=None)
            upcoming_event_groups = EventGroup.objects.filter(
                events__in=upcoming_events
            ).published()

            enrollable_single_events = upcoming_single_events.exclude(
                occurrences__enrolments__child=OuterRef("pk")
            )
            enrollable_event_groups = upcoming_event_groups.exclude(
                events__occurrences__enrolments__child=OuterRef("pk")
            )

            # Coalesce adds a default value for children which do not have enrollments
            # this year. Required for gte query filter to work.
            current_year_enrolment_count = Coalesce(
                Subquery(
                    enrolments.filter(
                        occurrence__time__year=now.year, child=OuterRef("pk")
                    )
                    .values("child")
                    .annotate(count=Count("pk"))
                    .values("count")
                ),
                0,
            )

            children_with_invitation = (
                children.filter(
                    Q(
                        Exists(enrollable_single_events)
                        | Exists(enrollable_event_groups)
                    )
                )
                .annotate(current_year_enrolment_count=current_year_enrolment_count)
                .exclude(
                    current_year_enrolment_count__gte=F("project__enrolment_limit")
                )
            )

            return guardians.filter(children__in=children_with_invitation).distinct()

        elif self.recipient_selection == Message.ENROLLED:
            return guardians.filter(
                children__enrolments__in=enrolments.filter(occurrence__time__gte=now)
            ).distinct()

        elif self.recipient_selection == Message.ATTENDED:
            return guardians.filter(
                children__enrolments__in=enrolments.filter(
                    occurrence__time__lt=now, attended=True
                )
            ).distinct()

        elif self.recipient_selection == Message.SUBSCRIBED_TO_FREE_SPOT_NOTIFICATION:
            return guardians.filter(
                children__free_spot_notification_subscriptions__in=subscriptions
            ).distinct()

        else:
            raise ValueError(
                f"Cannot send message {self} because of invalid recipient selection "
                f'value "{self.recipient_selection}".'
            )

    def can_user_administer(self, user):
        return user.can_administer_project(self.project)
