from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Optional

from django.apps import apps
from django.conf import settings
from django.db import models, transaction
from django.db.models import (
    Case,
    Count,
    Exists,
    ExpressionWrapper,
    F,
    OuterRef,
    Q,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Cast, Coalesce, ExtractYear, Greatest
from django.utils import timezone

from common.models import TranslatableQuerySet
from events.consts import MIN_SEATS_PER_ENROLMENT
from events.exceptions import NoFreePasswordsError

if TYPE_CHECKING:
    from children.models import Child
    from events.models import Event, TicketSystemPassword

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

    def with_enrolment_check_data(self):
        """
        Pre-annotate event groups with enrolment check data.

        Annotates:
        - `_group_year`: The calendar year of the group derived from earliest
          occurrence time or external event publish date.
        - `_published_event_count`: Number of published events in the group.
        - `_published_with_opening_time_count`: Count of published events with
          an explicit registration opening time.
        - `_earliest_opening_time`: Earliest registration opening time among
          published events in the group.
        """
        Occurrence = apps.get_model("events", "Occurrence")
        Event = apps.get_model("events", "Event")
        group_occ_year_subq = Subquery(
            Occurrence.objects.filter(
                event__event_group=OuterRef("pk"),
                event__ticket_system=Event.INTERNAL,
            )
            .order_by("time")
            .values(year=ExtractYear("time"))[:1]
        )
        group_ext_year_subq = Subquery(
            Event.objects.filter(event_group=OuterRef("pk"))
            .exclude(published_at=None)
            .exclude(ticket_system=Event.INTERNAL)
            .order_by("published_at", "id")
            .values(year=ExtractYear("published_at"))[:1]
        )
        published_events_q = Q(events__published_at__isnull=False)
        return self.annotate(
            _group_year=Coalesce(
                group_occ_year_subq,
                group_ext_year_subq,
                output_field=models.IntegerField(),
            ),
            _published_event_count=Count("events", filter=published_events_q),
            _published_with_opening_time_count=Count(
                "events__registration_opens_at", filter=published_events_q
            ),
            _earliest_opening_time=models.Min(
                "events__registration_opens_at", filter=published_events_q
            ),
        )


# This need to be inherited from TranslatableQuerySet instead of default model.QuerySet
class EventQueryset(TranslatableQuerySet):
    def user_can_view(self, user):
        # Published events are completely public (needed for public UI and
        # event organisers)
        published_q = Q(published_at__isnull=False)
        if not user.is_authenticated:
            return self.filter(published_q).distinct()

        # Unpublished events are only visible to system admins or the event's
        # organisation members
        admin_q = Q(project__in=user.administered_projects)
        if not user.is_system_administrator:
            admin_q &= Q(organisation__in=user.organisations.all())

        return self.filter(admin_q | published_q).distinct()

    def published(self):
        return self.filter(published_at__isnull=False)

    def unpublished(self):
        return self.filter(published_at__isnull=True)

    def upcoming(self, now=None):
        return self.filter(occurrences__time__gte=now or timezone.now()).distinct()

    def available(self, child):
        """
        Child's available events without checking yearly enrolment limits

        A child's available events must match all the following rules:
            * the event must be published
            * the event must have at least one occurrence in the future
            * the child must not have enrolled to the event
            * the child must not have enrolled to any event in the same event group
              as the event

        :note: Does NOT take yearly enrolment limits into account
        """
        EventGroup = apps.get_model("events", "EventGroup")
        child_enrolled_event_groups = EventGroup.objects.filter(
            events__occurrences__in=child.occurrences.all()
        )
        return (
            self.published()
            .upcoming()
            .exclude(occurrences__in=child.occurrences.all())
            .exclude(event_group__in=child_enrolled_event_groups)
        )


class OccurrenceQueryset(models.QuerySet):
    def user_can_view(self, user):
        # Occurrence visibility mirrors Event visibility
        published_q = Q(event__published_at__isnull=False)
        if not user.is_authenticated:
            return self.filter(published_q).distinct()

        admin_q = Q(event__project__in=user.administered_projects)
        if not user.is_system_administrator:
            admin_q &= Q(event__organisation__in=user.organisations.all())

        return self.filter(admin_q | published_q).distinct()

    def delete(self, *args, **kwargs):
        for obj in self:
            obj.delete()

    def send_free_spot_notifications_if_needed(self):
        for obj in self:
            obj.send_free_spot_notifications_if_needed()

    def upcoming(self, now=None):
        return self.filter(time__gte=now or timezone.now())

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

    def in_any_language(self, alpha_3_codes):
        """
        Return occurrences that have at least one of the given languages.

        :param alpha_3_codes: Lowercase ISO 639-3 (alpha-3) codes.
        """
        OccurrenceLanguage = apps.get_model("events", "OccurrenceLanguage")
        return self.filter(
            Exists(
                OccurrenceLanguage.objects.filter(
                    occurrence=OuterRef("pk"),
                    language__alpha_3_code__in=alpha_3_codes,
                )
            )
        )

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

    def with_enrolment_count(self):
        return self.annotate(enrolment_count=Count("enrolments", distinct=True))

    def with_attended_enrolment_count(self):
        return self.annotate(
            attended_enrolment_count=Count(
                "enrolments", Q(enrolments__attended=True), distinct=True
            )
        )

    def with_handled_enrolment_count(self):
        """
        Annotate occurrences with `handled_enrolment_count`: the number of
        enrolments whose attendance has been processed (`attended` is True or False).
        """
        return self.annotate(
            handled_enrolment_count=Count(
                "enrolments", Q(enrolments__attended__isnull=False), distinct=True
            )
        )

    @staticmethod
    def _enrolment_sum_subquery(expression, **extra_filters):
        Enrolment = apps.get_model("events", "Enrolment")
        subquery = (
            Enrolment.objects.filter(occurrence=OuterRef("pk"), **extra_filters)
            .order_by()
            .values("occurrence")
            .annotate(total=Sum(expression))
            .values("total")
        )
        return Coalesce(
            Subquery(subquery, output_field=models.IntegerField()), Value(0)
        )

    @staticmethod
    def _override_or_calculated(override_expr, calculated_expr):
        override_case = Case(
            When(
                attended_children_count_override__isnull=False,
                attended_adults_count_override__isnull=False,
                then=override_expr,
            ),
            default=None,
            output_field=models.IntegerField(),
        )
        return Coalesce(
            override_case, calculated_expr, output_field=models.IntegerField()
        )

    def _with_enrolment_sum(self, annotation_name: str, expression, **extra_filters):
        return self.annotate(
            **{
                annotation_name: self._enrolment_sum_subquery(
                    expression, **extra_filters
                )
            }
        )

    def _with_attended_participant_count(
        self, annotation_name: str, expression, override_field: str
    ):
        calculated = self._enrolment_sum_subquery(expression)
        return self.annotate(
            **{
                annotation_name: self._override_or_calculated(
                    F(override_field), calculated
                )
            }
        )

    def with_attended_children_count(self):
        return self._with_attended_participant_count(
            "attended_children_count",
            EnrolmentQueryset.arrived_children_expression(),
            "attended_children_count_override",
        )

    def with_attended_adults_count(self):
        return self._with_attended_participant_count(
            "attended_adults_count",
            EnrolmentQueryset.arrived_adults_expression(),
            "attended_adults_count_override",
        )

    def with_enrolled_children_count(self):
        return self._with_enrolment_sum(
            "enrolled_children_count", EnrolmentQueryset.children_expression()
        )

    def with_enrolled_adults_count(self):
        return self._with_enrolment_sum(
            "enrolled_adults_count", EnrolmentQueryset.adults_expression()
        )

    def with_attended_seats(self):
        """
        Annotate occurrences with arrived seat counts:
        - `calculated_attended_seats`: sum of arrived physical seats across enrolments.
        - `attended_seats`: the sum of the children and adults count overrides
          when set, otherwise `calculated_attended_seats`.
        """
        return self.annotate(
            calculated_attended_seats=self._enrolment_sum_subquery(
                EnrolmentQueryset.arrived_seats_expression()
            )
        ).annotate(
            attended_seats=self._override_or_calculated(
                Cast(F("attended_children_count_override"), models.IntegerField())
                + F("attended_adults_count_override"),
                "calculated_attended_seats",
            )
        )

    def with_pending_arrival_seats(self):
        """
        Annotate occurrences with `pending_arrival_seats`: the total booked
        physical seats of enrolments not yet marked arrived or absent
        (`attended` is NULL).
        """
        return self._with_enrolment_sum(
            "pending_arrival_seats",
            EnrolmentQueryset.seats_expression(),
            attended__isnull=True,
        )

    def with_reserved_seats(self):
        return self._with_enrolment_sum(
            "reserved_seats", EnrolmentQueryset.seats_expression()
        )

    def with_remaining_capacity(self):
        """
        Annotate occurrences with remaining seat capacity.

        Calculates `remaining_capacity` as effective capacity minus reserved
        seats, floored at 0.
        """
        return self.with_reserved_seats().annotate(
            remaining_capacity=Greatest(
                Coalesce(
                    "capacity_override",
                    "event__capacity_per_occurrence",
                    Value(0),
                )
                - F("reserved_seats"),
                Value(0),
                output_field=models.IntegerField(),
            )
        )

    def with_free_spot_notification_subscription_count(self):
        return self.annotate(
            free_spot_notification_subscription_count=Count(
                "free_spot_notification_subscriptions", distinct=True
            )
        )

    def with_doorway_metrics(self, *, include_remaining_capacity: bool = True):
        """
        Annotate occurrences with doorway arrival and capacity metrics used by
        GraphQL resolvers (`OccurrenceNode` and ticket verification).
        """
        qs = (
            self.with_enrolment_count()
            .with_attended_enrolment_count()
            .with_handled_enrolment_count()
            .with_attended_seats()
            .with_pending_arrival_seats()
        )
        if include_remaining_capacity:
            return qs.with_remaining_capacity()
        return qs.with_reserved_seats()

    def with_report_metrics(self):
        """
        Annotate occurrences with participant and attendance metrics used by
        the Reports REST API. `attended_seats` and `reserved_seats` are derived
        by `Occurrence` from the annotated children and adults counts.
        """
        return (
            self.with_enrolment_count()
            .with_enrolled_children_count()
            .with_enrolled_adults_count()
            .with_attended_enrolment_count()
            .with_attended_children_count()
            .with_attended_adults_count()
            .with_free_spot_notification_subscription_count()
        )


class EnrolmentQueryset(models.QuerySet):
    @staticmethod
    def _booked_participant_expression(extra_field: str):
        return Value(1, output_field=models.IntegerField()) + Coalesce(
            extra_field, Value(0), output_field=models.IntegerField()
        )

    @staticmethod
    def children_expression():
        return EnrolmentQueryset._booked_participant_expression("extra_children_count")

    @staticmethod
    def adults_expression():
        return EnrolmentQueryset._booked_participant_expression("extra_guardians_count")

    @staticmethod
    def seats_expression():
        """
        Return a SQL expression calculating the total booked physical seats for an
        enrolment: `MIN_SEATS_PER_ENROLMENT` (1 default child + 1 default guardian = 2)
        plus `extra_children_count` and `extra_guardians_count` (treating NULL as 0).
        """
        return (
            Value(MIN_SEATS_PER_ENROLMENT, output_field=models.IntegerField())
            + Coalesce(
                "extra_children_count",
                Value(0),
                output_field=models.IntegerField(),
            )
            + Coalesce(
                "extra_guardians_count",
                Value(0),
                output_field=models.IntegerField(),
            )
        )

    @staticmethod
    def _arrived_participant_expression(arrived_field: str, fallback_expr):
        return Case(
            When(
                arrived_children_count__isnull=False,
                arrived_guardians_count__isnull=False,
                then=F(arrived_field),
            ),
            When(attended=True, then=fallback_expr),
            default=Value(0),
            output_field=models.IntegerField(),
        )

    @staticmethod
    def arrived_children_expression():
        return EnrolmentQueryset._arrived_participant_expression(
            "arrived_children_count", EnrolmentQueryset.children_expression()
        )

    @staticmethod
    def arrived_adults_expression():
        return EnrolmentQueryset._arrived_participant_expression(
            "arrived_guardians_count", EnrolmentQueryset.adults_expression()
        )

    @staticmethod
    def arrived_seats_expression():
        """
        Return a SQL expression calculating the arrived physical seats for an
        enrolment: `arrived_children_count + arrived_guardians_count` when both are
        present, falling back to booked `seats_expression()` when `attended=True`
        without explicit arrived counts (legacy rows), or 0 otherwise.
        """
        return Case(
            When(
                arrived_children_count__isnull=False,
                arrived_guardians_count__isnull=False,
                then=F("arrived_children_count") + F("arrived_guardians_count"),
            ),
            When(attended=True, then=EnrolmentQueryset.seats_expression()),
            default=Value(0),
            output_field=models.IntegerField(),
        )

    def user_can_view(self, user):
        if not user.is_authenticated:
            return self.none()

        # Enrolments (and attendee lists) are strictly restricted.
        # They are NEVER globally visible, regardless of the event's published status.
        guardian_q = Q(child__guardians__user=user)
        admin_q = Q(child__project__in=user.administered_projects)
        if not user.is_system_administrator:
            admin_q &= Q(occurrence__event__organisation__in=user.organisations.all())

        return self.filter(guardian_q | admin_q).distinct()

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


class TicketSystemPasswordQueryset(models.QuerySet):
    def free(self):
        return self.filter(assigned_at=None, child=None)

    def used(self):
        return self.exclude(assigned_at=None)

    @transaction.atomic
    def assign(self, event: Event, child: Child) -> TicketSystemPassword:
        obj: Optional[TicketSystemPassword] = (
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

        obj.assign(child)

        return obj

    def event_upcoming_or_ongoing(self):
        return self.exclude(event__published_at__isnull=True).filter(
            Q(event__ticket_system_end_time__isnull=True)
            | Q(event__ticket_system_end_time__gte=timezone.now())
        )
