from datetime import datetime, time

import django_filters
import graphene
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Case, Exists, F, OuterRef, Prefetch, Q, Subquery, When
from django.db.models.functions import Coalesce, ExtractYear
from django.utils import timezone as django_utils_timezone
from django.utils.timezone import make_aware
from graphene_django.filter import ListFilter, TypedFilter
from graphql_relay import from_global_id

from children.cache import ChildRequestCache
from children.models import Child
from common.utils import get_node_id_from_global_id, year_of
from events.consts import MIN_SEATS_PER_ENROLMENT
from events.models import (
    Event,
    EventGroup,
    Occurrence,
    TicketSystemPassword,
)
from events.utils import convert_to_localtime_tz
from kukkuu.exceptions import ApiUsageError


class OccurrenceFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(lookup_expr="date", field_name="time")
    time = django_filters.TimeFilter(method="filter_by_time", field_name="time")
    upcoming = django_filters.BooleanFilter(method="filter_by_upcoming")
    upcoming_with_leeway = django_filters.BooleanFilter(
        method="filter_by_upcoming_with_leeway"
    )
    upcoming_with_ongoing = django_filters.BooleanFilter(
        method="filter_by_upcoming_with_ongoing"
    )
    venue_id = django_filters.CharFilter(
        field_name="venue", method="filter_by_venue_global_id"
    )
    event_id = django_filters.CharFilter(
        field_name="event", method="filter_by_event_global_id"
    )
    occurrence_language = django_filters.CharFilter(
        field_name="occurrence_language", method="filter_by_occurrence_language"
    )
    project_id = django_filters.Filter(method="filter_by_project_global_id")

    class Meta:
        model = Occurrence
        fields = [
            "date",
            "time",
            "upcoming",
            "upcoming_with_leeway",
            "venue_id",
            "event_id",
            "occurrence_language",
        ]

    def filter_by_time(self, qs, name, value):
        value = convert_to_localtime_tz(value)
        return qs.filter(**{name + "__time": value})

    def filter_by_upcoming(self, qs, name, value):
        if value:
            return qs.upcoming()
        return qs

    def filter_by_upcoming_with_leeway(self, qs, name, value):
        if value:
            return qs.upcoming_with_leeway()
        return qs

    def filter_by_upcoming_with_ongoing(self, qs, name, value):
        if value:
            return qs.upcoming_with_ongoing()
        return qs

    def filter_by_venue_global_id(self, qs, name, value):
        venue_id = from_global_id(value)[1]
        return qs.filter(venue_id=venue_id)

    def filter_by_event_global_id(self, qs, name, value):
        event_id = from_global_id(value)[1]
        return qs.filter(event_id=event_id)

    def filter_by_occurrence_language(self, qs, name, value):
        return qs.filter(occurrence_language=value.lower())

    def filter_by_project_global_id(self, qs, name, value):
        node_id = get_node_id_from_global_id(value, "ProjectNode")
        return qs.filter(event__project_id=node_id) if node_id else qs.none()


class EventFilter(django_filters.FilterSet):
    available_for_child = django_filters.CharFilter(
        method="filter_by_available_for_child"
    )
    upcoming = django_filters.BooleanFilter(method="filter_by_upcoming")
    theme_path = django_filters.CharFilter(
        field_name="theme_paths__slug", help_text="Slug of the theme path."
    )
    child_id = TypedFilter(input_type=graphene.ID, method="noop_filter")
    available_only = django_filters.BooleanFilter(method="noop_filter")
    start_date = django_filters.DateFilter(method="noop_filter")
    languages = ListFilter(
        input_type=graphene.List(graphene.String), method="noop_filter"
    )
    theme_paths = ListFilter(
        input_type=graphene.List(graphene.String), method="noop_filter"
    )
    # Accessibility placeholder until venue accessibility filtering is implemented.
    accessibility = ListFilter(
        input_type=graphene.List(graphene.String), method="filter_accessibility"
    )
    family_only = django_filters.BooleanFilter(method="noop_filter")

    # Filters that require `child_id` (enforced in filter_queryset) and are handled
    # by _apply_child_search(). Update this tuple when adding or removing child-specific
    # search filters.
    SEARCH_ONLY_ARGS = (
        "available_only",
        "start_date",
        "languages",
        "theme_paths",
        "accessibility",
        "family_only",
    )

    class Meta:
        model = Event
        fields = [
            "project_id",
            "available_for_child",
            "upcoming",
            "theme_path",
            "child_id",
            "available_only",
            "start_date",
            "languages",
            "theme_paths",
            "accessibility",
            "family_only",
        ]

    def noop_filter(self, qs, name, value):
        """No-op filter placeholder returning the queryset unmodified."""
        return qs

    def filter_accessibility(self, qs, name, value):
        """
        Validate and filter events by accessibility criteria.

        Venue accessibility filtering is not yet implemented. Any request
        specifying nonempty accessibility criteria is rejected via ApiUsageError,
        while empty or omitted values return the queryset unmodified.

        :param qs: Base Event QuerySet.
        :param name: Filter field name ("accessibility").
        :param value: List of requested accessibility filter values.
        :return: Unmodified Event QuerySet if value is empty.
        :raises ApiUsageError: If nonempty accessibility criteria are requested.
        """
        if value and any(v for v in value if str(v).strip()):
            raise ApiUsageError("Accessibility filtering is not yet supported.")
        return qs

    def filter_by_available_for_child(self, qs, name, value):
        """Filter events available for the child decoded from global ID."""
        child_id = get_node_id_from_global_id(value, "ChildNode")
        try:
            child = Child.objects.user_can_view(self.request.user).get(id=child_id)
        except Child.DoesNotExist:
            return qs
        except (ValidationError, ValueError):
            return qs.none()
        return qs.available(child)

    def filter_by_upcoming(self, qs, name, value):
        """Filter events to upcoming events when value is truthy."""
        if value:
            return qs.upcoming()
        return qs

    def _get_search_child(self) -> Child | None:
        """Fetch and prefetch the Child instance specified by child_id."""
        raw_child_id = self.data.get("child_id") or ""
        node_id = get_node_id_from_global_id(raw_child_id, "ChildNode")
        if not node_id:
            return None
        try:
            return (
                Child.objects.user_can_view(self.request.user)
                .select_related("project")
                .prefetch_related(
                    "occurrences__event",
                    "ticket_system_passwords__event",
                )
                .get(id=node_id)
            )
        except (Child.DoesNotExist, ValidationError, ValueError):
            return None

    def filter_queryset(self, queryset):
        """
        Coordinate query filtering, child validation, prefetching, and caching.

        This method orchestrates the event search pipeline:
        1. Search Argument Guard:
           Ensures child-specific search arguments (availableOnly, startDate,
           languages, themePaths, accessibility, familyOnly) are only used
           when `childId` is provided. Raises ApiUsageError if search arguments
           are provided without childId.
        2. Backward Compatibility:
           If no `childId` is passed, delegates to standard
           `super().filter_queryset(queryset)` for legacy/admin event queries.
        3. Permission Check & Safe Fallback:
           Decodes the child global Relay ID and fetches the Child using
           `Child.objects.user_can_view(self.request.user)`. If the child does
           not exist, the ID is invalid, or the user lacks permission to view
           the child, returns `queryset.none()` to ensure complete data
           isolation without leaking information.
        4. Eager Prefetching & Request Memoization:
           Prefetches `project`, `occurrences__event`, and
           `ticket_system_passwords__event`. Caches the prefetched child via
           `ChildRequestCache.set(self.request, child)`, which is shared with GraphQL
           field resolvers (e.g. enrolmentDeniedReason, canChildEnroll, childPassword).
           This eliminates N+1 database queries across returned event nodes.
        5. Child-Specific Search:
           Applies publishing rules, project boundary filtering, search
           arguments, and availability constraints via `_apply_child_search`.

        :param queryset: Base Event QuerySet.
        :return: Filtered Event QuerySet for the given child and filters.
        :raises ApiUsageError: If child search filters are passed without childId.
        """
        has_child_id = "child_id" in self.data and self.data.get("child_id") is not None
        has_search_args = any(self.data.get(k) for k in self.SEARCH_ONLY_ARGS)
        if has_search_args and not has_child_id:
            raise ApiUsageError("Child-specific search filters require childId.")

        if not has_child_id:
            return super().filter_queryset(queryset)

        child = self._get_search_child()
        if not child:
            return queryset.none()

        qs = super().filter_queryset(queryset)
        if self.request is not None:
            ChildRequestCache.set(self.request, child)

        return self._apply_child_search(qs, child)

    def _apply_child_search(self, qs, child: Child):
        """
        Filter, annotate, and order events suitable for the given child.

        Constructs a common base search query first (scoping to project, publishing,
        prefetching occurrences, annotations, and chronological ordering), then
        updates it with filter-specific criteria (family, theme paths, occurrence
        criteria, and child eligibility).

        :param qs: Base Event QuerySet.
        :param child: Prefetched Child instance.
        :return: Filtered, annotated, and ordered Event QuerySet.
        """
        now = django_utils_timezone.now()
        qs = self._get_common_search_query(qs, child, now)

        if self.form.cleaned_data.get("family_only"):
            qs = self._apply_family_only(qs)

        theme_paths = [
            slug for slug in (self.form.cleaned_data.get("theme_paths") or []) if slug
        ]
        if theme_paths:
            qs = self._apply_theme_paths(qs, theme_paths)

        start_date = self.form.cleaned_data.get("start_date")
        languages = [
            lang.lower()
            for lang in (self.form.cleaned_data.get("languages") or [])
            if lang
        ]
        available_only = bool(self.form.cleaned_data.get("available_only"))
        if start_date or languages or available_only:
            qs = self._apply_occurrence_filters(
                qs,
                now,
                start_date=start_date,
                languages=languages,
                available_only=available_only,
            )

        if available_only:
            qs = self._apply_child_eligibility(
                qs,
                child,
                now,
                start_date=start_date,
                languages=languages,
            )

        return qs

    def _get_common_search_query(self, qs, child: Child, now):
        """
        Build the common base search query for a child.

        Applies project scoping, published/upcoming constraints, event group
        visibility, prefetching of occurrences with capacities, annotations for
        sorting and ticket availability, and default chronological ordering.

        :param qs: Base Event QuerySet.
        :param child: Prefetched Child instance.
        :param now: Current timezone-aware datetime.
        :return: Annotated and ordered base Event QuerySet with prefetched
            occurrences and relations.
        """
        earliest_upcoming = Subquery(
            Occurrence.objects.filter(event=OuterRef("pk"), time__gte=now)
            .order_by("time")
            .values("time")[:1]
        )
        first_occ_year = Subquery(
            Occurrence.objects.filter(event=OuterRef("pk"))
            .order_by("time")
            .values(year=ExtractYear("time"))[:1]
        )
        VenueTranslation = apps.get_model("venues", "VenueTranslation")

        return (
            qs.published()
            .upcoming()
            .filter(project_id=child.project_id)
            .filter(
                Q(event_group__isnull=True) | Q(event_group__published_at__isnull=False)
            )
            .select_related("project")
            .prefetch_related(
                Prefetch(
                    "event_group",
                    queryset=EventGroup.objects.with_enrolment_check_data(),
                ),
                Prefetch(
                    "occurrences",
                    queryset=Occurrence.objects.user_can_view(self.request.user)
                    .upcoming()
                    .with_end_time()
                    .with_enrolment_count()
                    .with_attended_enrolment_count()
                    .with_reserved_seats()
                    .with_remaining_capacity()
                    .with_free_spot_notification_subscription_count()
                    .order_by("time")
                    .select_related(
                        "event", "event__project", "venue", "venue__project"
                    )
                    .prefetch_related(
                        Prefetch(
                            "venue__translations",
                            queryset=VenueTranslation.objects.order_by("language_code"),
                        )
                    ),
                    to_attr="_prefetched_upcoming_occurrences",
                ),
            )
            .annotate(
                _first_occurrence_year=first_occ_year,
                _has_free_passwords=Exists(
                    TicketSystemPassword.objects.free().filter(event=OuterRef("pk"))
                ),
                _sort_time=Coalesce(
                    earliest_upcoming, "registration_opens_at", "published_at"
                ),
            )
            .order_by("_sort_time", "pk")
        )

    def _apply_family_only(self, qs):
        """
        Filter events to only those configured for family attendance.

        Restricts events to `participants_per_invite == Event.FAMILY`.

        :param qs: Event QuerySet to filter.
        :return: Filtered Event QuerySet.
        """
        return qs.filter(participants_per_invite=Event.FAMILY)

    def _apply_theme_paths(self, qs, theme_paths: list[str]):
        """
        Filter events tagged with any of the specified theme path slugs.

        Uses an `Exists` subquery against the theme paths many-to-many through
        table to avoid duplicate rows and distinct() overhead.

        :param qs: Event QuerySet to filter.
        :param theme_paths: List of theme path slug strings to match.
        :return: Filtered Event QuerySet.
        """
        return qs.filter(
            Exists(
                Event.theme_paths.through.objects.filter(
                    event_id=OuterRef("pk"),
                    theme_path_id__in=theme_paths,
                )
            )
        )

    def _get_matching_occurrences_qs(self, now, *, start_date=None, languages=None):
        """
        Build an upcoming occurrences subquery matching start date and languages.

        :param now: Current timezone-aware datetime.
        :param start_date: Optional minimum occurrence date (date object).
        :param languages: Optional list of lowercase ISO language codes.
        :return: Occurrence QuerySet suitable for use in an Exists subquery.
        """
        occ_qs = Occurrence.objects.filter(event=OuterRef("pk"), time__gte=now)
        if start_date:
            start_dt = make_aware(datetime.combine(start_date, time.min))
            occ_qs = occ_qs.filter(time__gte=start_dt)
        if languages:
            occ_qs = occ_qs.filter(occurrence_language__in=languages)
        return occ_qs

    def _apply_occurrence_filters(
        self, qs, now, *, start_date, languages, available_only
    ):
        """
        Filter events by occurrence-level criteria: date, language, and availability.

        Builds an upcoming-occurrence subquery (`occ_qs`) for `start_date` and
        `languages` so that an event only matches if at least one single upcoming
        occurrence satisfies all requested date and language criteria simultaneously
        (e.g. an event with Swedish on Monday and English on Tuesday only matches
        `languages=['sv']` + `startDate=Tuesday` if Swedish is on Tuesday).

        When `available_only=False`:
        - Both internal and external events must have at least one upcoming
          occurrence matching `occ_qs`.

        When `available_only=True`:
        - Internal ticket system events (`Event.INTERNAL`) must have at least one
          upcoming occurrence matching `occ_qs` that also has remaining seat
          capacity >= `MIN_SEATS_PER_ENROLMENT` (2 seats).
        - External ticket system events (Ticketmaster, Lippupiste, Tixly) do not
          track seat capacity on occurrences; instead, they require at least one
          unassigned `TicketSystemPassword` (`has_free_pw`), plus a matching
          occurrence in `occ_qs` if `start_date` or `languages` was specified.

        :param qs: Event QuerySet to filter.
        :param now: Current timezone-aware datetime.
        :param start_date: Optional minimum occurrence date (date object).
        :param languages: Optional list of lowercase ISO language codes.
        :param available_only: Whether to restrict to events with available
            capacity (internal) or unassigned passwords (external).
        :return: Filtered Event QuerySet.
        """
        occ_qs = self._get_matching_occurrences_qs(
            now, start_date=start_date, languages=languages
        )

        # When available_only=False, this method is only invoked if start_date or
        # languages was requested. Both internal and external events must have an
        # occurrence satisfying the requested occurrence-level criteria.
        if not available_only:
            return qs.filter(Exists(occ_qs))

        internal_occ_qs = occ_qs.with_remaining_capacity().filter(
            remaining_capacity__gte=MIN_SEATS_PER_ENROLMENT
        )
        has_free_pw = Exists(
            TicketSystemPassword.objects.free().filter(event=OuterRef("pk"))
        )
        external_q = ~Q(ticket_system=Event.INTERNAL) & has_free_pw & Exists(occ_qs)

        return qs.filter(
            (Q(ticket_system=Event.INTERNAL) & Exists(internal_occ_qs)) | external_q
        )

    def _apply_child_eligibility(
        self, qs, child: Child, now, *, start_date=None, languages=None
    ):
        """
        Exclude events the child cannot enroll in when availableOnly=True.

        Excludes:
        - Events child is already enrolled in or has passwords for.
        - Events in event groups where the child is already enrolled.
        - Events whose registration has not opened yet.
        - Events in years where child reached the annual project enrolment limit.

        :param qs: Event QuerySet to filter.
        :param child: Prefetched Child instance.
        :param now: Current timezone-aware datetime.
        :param start_date: Optional minimum occurrence date (date object).
        :param languages: Optional list of lowercase ISO language codes.
        :return: Filtered Event QuerySet containing only events the child can
            enroll in.
        """
        enrolled_event_ids = child.get_enrolled_event_ids()
        if enrolled_event_ids:
            qs = qs.exclude(id__in=enrolled_event_ids)

        passwords = child.get_ticket_system_passwords_by_event_id()
        if passwords:
            qs = qs.exclude(id__in=passwords.keys())

        ineligible_group_ids = (
            child.get_enrolled_event_group_ids()
            | child.get_ticket_system_password_event_group_ids()
        )
        if ineligible_group_ids:
            qs = qs.exclude(event_group_id__in=ineligible_group_ids)

        qs = qs.filter(
            Q(registration_opens_at__isnull=True) | Q(registration_opens_at__lte=now)
        )

        return self._filter_enrolment_limits(
            qs, child, now, start_date=start_date, languages=languages
        )

    def _filter_enrolment_limits(
        self, qs, child: Child, now, *, start_date=None, languages=None
    ):
        """
        Exclude events in years where child reached the project enrolment limit.

        Determines the calendar year of each event:
        - Internal ticketing: Year of the first occurrence, plus the year of the
          matching upcoming available occurrence.
        - External ticketing: Year of `published_at`.
        - Event groups: Year of the earliest occurrence across the group, or
          earliest `published_at` of an external event in the group.

        If the child's enrolment count in that year meets or exceeds the project
        `enrolment_limit` (typically 2 enrolments per year), the event is
        excluded.

        :param qs: Event QuerySet to filter.
        :param child: Prefetched Child instance.
        :param now: Current timezone-aware datetime.
        :param start_date: Optional minimum occurrence date (date object).
        :param languages: Optional list of lowercase ISO language codes.
        :return: Filtered Event QuerySet excluding full years.
        """
        enrolment_limit = child.project.enrolment_limit
        if enrolment_limit <= 0:
            return qs.none()

        all_years = {year_of(occ.time) for occ in child.occurrences.all()} | {
            year_of(pw.event.published_at)
            for pw in child.ticket_system_passwords.all()
            if pw.event and pw.event.published_at
        }
        full_years = {
            year
            for year in all_years
            if child.get_enrolment_count(year=year) >= enrolment_limit
        }
        if not full_years:
            return qs

        available_internal_occ_qs = (
            self._get_matching_occurrences_qs(
                now, start_date=start_date, languages=languages
            )
            .with_remaining_capacity()
            .filter(remaining_capacity__gte=MIN_SEATS_PER_ENROLMENT)
            .exclude(time__year__in=full_years)
        )
        group_occ_year_subq = Subquery(
            Occurrence.objects.filter(event__event_group=OuterRef("event_group_id"))
            .order_by("time")
            .values(year=ExtractYear("time"))[:1]
        )
        group_ext_year_subq = Subquery(
            Event.objects.filter(event_group=OuterRef("event_group_id"))
            .exclude(published_at=None)
            .exclude(ticket_system=Event.INTERNAL)
            .order_by("published_at", "id")
            .values(year=ExtractYear("published_at"))[:1]
        )
        return (
            qs.annotate(
                _event_year=Case(
                    When(
                        ticket_system=Event.INTERNAL,
                        then=F("_first_occurrence_year"),
                    ),
                    default=ExtractYear("published_at"),
                    output_field=models.IntegerField(),
                ),
                _group_year=Coalesce(
                    group_occ_year_subq,
                    group_ext_year_subq,
                    output_field=models.IntegerField(),
                ),
            )
            .exclude(_event_year__in=full_years)
            .exclude(event_group__isnull=False, _group_year__in=full_years)
            .filter(
                ~Q(ticket_system=Event.INTERNAL) | Exists(available_internal_occ_qs)
            )
        )
