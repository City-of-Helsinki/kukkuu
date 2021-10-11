from functools import reduce

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_ilmoitin.utils import Message as MailerMessage
from django_ilmoitin.utils import send_all, send_mail
from parler.models import TranslatedFields
from parler.utils.context import switch_language

from children.models import Child
from common.models import TimestampedModel, TranslatableModel, TranslatableQuerySet
from events.models import Enrolment, Event, Occurrence
from projects.models import Project
from subscriptions.models import FreeSpotNotificationSubscription
from users.models import Guardian


class AlreadySentError(Exception):
    pass


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
        if self.sent_at and not force:
            raise AlreadySentError()

        guardians = self.get_recipient_guardians()

        self.sent_at = timezone.now()
        self.recipient_count = len(guardians)

        with transaction.atomic():
            self.save(update_fields=("sent_at", "recipient_count"))

            for guardian in guardians:
                with switch_language(self, guardian.language):

                    # hopefully this functionality that uses django-ilmoitin's internals
                    # is only temporarily here, and will be removed when either
                    # 1) we need to use a notification template and thus will use
                    #    ilmoitin's regular send_notification(), or
                    # 2) support for sending a mail without a notification template will
                    #    be added to ilmoitin and we can use that
                    if guardian.language in getattr(
                        settings, "ILMOITIN_TRANSLATED_FROM_EMAIL", {}
                    ):
                        from_email = settings.ILMOITIN_TRANSLATED_FROM_EMAIL[
                            guardian.language
                        ]
                    else:
                        from_email = settings.DEFAULT_FROM_EMAIL

                    send_mail(
                        self.subject,
                        self.body_text,
                        guardian.email,
                        from_email=from_email,
                    )

        if not getattr(settings, "ILMOITIN_QUEUE_NOTIFICATIONS", False):
            MailerMessage.objects.retry_deferred()
            send_all()

    def get_recipient_guardians(self):
        guardians = Guardian.objects.filter(children__project=self.project)

        if self.recipient_selection == Message.ALL:
            return guardians.distinct()

        now = timezone.now()
        upcoming_events = Event.objects.filter(
            project=self.project, occurrences__time__gte=now
        ).published()
        if self.event_id:
            upcoming_events = upcoming_events.filter(pk=self.event_id)

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
            if not upcoming_events.exists():
                return Guardian.objects.none()

            children_enrolled_to_every_upcoming_event = reduce(
                lambda x, y: x.filter(occurrences__event=y), upcoming_events, children
            )
            children_with_invitation = children.exclude(
                pk__in=children_enrolled_to_every_upcoming_event.values("pk")
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
