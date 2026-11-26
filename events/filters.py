import django_filters
import graphene
from graphene_django.filter import ListFilter, TypedFilter
from graphql_relay import from_global_id

from children.cache import ChildRequestCache
from common.utils import get_node_id_from_global_id
from events.models import Event, Occurrence
from events.search_service import EventSearchService
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
    languages = ListFilter(
        input_type=graphene.List(graphene.String),
        method="filter_by_languages",
        label="ISO 639-3 (alpha-3) codes. Matches occurrences with any of them.",
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
            "languages",
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

    def filter_by_languages(self, qs, name, value):
        if not value:
            return qs
        return qs.in_any_language([code.lower() for code in value if code])

    def filter_by_project_global_id(self, qs, name, value):
        node_id = get_node_id_from_global_id(value, "ProjectNode")
        return qs.filter(event__project_id=node_id) if node_id else qs.none()


class EventFilter(django_filters.FilterSet):
    upcoming = django_filters.BooleanFilter(method="filter_by_upcoming")
    theme_path = django_filters.CharFilter(
        field_name="theme_paths__slug", help_text="Slug of the theme path."
    )
    child_id = TypedFilter(input_type=graphene.ID, method="noop_filter")
    has_free_spots = django_filters.BooleanFilter(method="noop_filter")
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
    # by EventSearchService.search(). Update this tuple when adding or removing
    # child-specific search filters.
    SEARCH_ONLY_ARGS = (
        "has_free_spots",
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
            "upcoming",
            "theme_path",
            "child_id",
            "has_free_spots",
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

    def filter_by_upcoming(self, qs, name, value):
        """Filter events to upcoming events when value is truthy."""
        if value:
            return qs.upcoming()
        return qs

    def filter_queryset(self, queryset):
        """
        Coordinate query filtering, child validation, prefetching, and caching.

        This method orchestrates the event search pipeline:
        1. Search Argument Guard:
           Ensures child-specific search arguments (hasFreeSpots, startDate,
           languages, themePaths, accessibility, familyOnly) are only used
           when `childId` is provided. Raises ApiUsageError if search arguments
           are provided without childId.
        2. Backward Compatibility:
           If no `childId` is passed, delegates to standard
           `super().filter_queryset(queryset)` for legacy/admin event queries.
        3. Permission Check & Safe Fallback:
           Decodes the child global Relay ID and fetches the Child using
           `EventSearchService.get_search_child`. If the child does not exist,
           the ID is invalid, or the user lacks permission to view the child,
           returns `queryset.none()` to ensure complete data isolation without
           leaking information.
        4. Eager Prefetching & Request Memoization:
           Caches the prefetched child via `ChildRequestCache.set(self.request, child)`,
           which is shared with GraphQL field resolvers (e.g. enrolmentDeniedReason,
           canChildEnroll, childPassword). This eliminates N+1 database queries
           across returned event nodes.
        5. Child-Specific Search:
           Applies publishing rules, project boundary filtering, search
           arguments, and free-space constraints via `EventSearchService.search`.

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

        child = EventSearchService.get_search_child(
            self.request.user, self.data.get("child_id") or ""
        )
        if not child:
            return queryset.none()

        qs = super().filter_queryset(queryset)
        if self.request is not None:
            ChildRequestCache.set(self.request, child)

        return EventSearchService.search(
            qs,
            child=child,
            user=self.request.user,
            family_only=bool(self.form.cleaned_data.get("family_only")),
            theme_paths=self.form.cleaned_data.get("theme_paths"),
            start_date=self.form.cleaned_data.get("start_date"),
            languages=self.form.cleaned_data.get("languages"),
            has_free_spots=bool(self.form.cleaned_data.get("has_free_spots")),
        )
