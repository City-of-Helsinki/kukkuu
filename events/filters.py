import django_filters
from graphql_relay import from_global_id

from children.models import Child
from common.utils import get_node_id_from_global_id
from events.models import Event, Occurrence
from events.utils import convert_to_localtime_tz


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

    class Meta:
        model = Event
        fields = [
            "project_id",
            "available_for_child",
        ]

    def filter_by_available_for_child(self, qs, name, value):
        child_id = get_node_id_from_global_id(value, "ChildNode")
        try:
            child = Child.objects.user_can_view(self.request.user).get(id=child_id)
        except Child.DoesNotExist:
            return qs
        return qs.available(child)

    def filter_by_upcoming(self, qs, name, value):
        if value:
            return qs.upcoming()
        return qs
