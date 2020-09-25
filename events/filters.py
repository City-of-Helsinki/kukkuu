from datetime import timedelta

import django_filters
from django.conf import settings
from django.utils import timezone
from graphql_relay import from_global_id

from common.utils import get_node_id_from_global_id
from events.models import Occurrence
from events.utils import convert_to_localtime_tz


class OccurrenceFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(lookup_expr="date", field_name="time")
    time = django_filters.TimeFilter(method="filter_by_time", field_name="time")
    upcoming = django_filters.BooleanFilter(
        method="filter_by_upcoming", field_name="time"
    )
    upcoming_with_leeway = django_filters.BooleanFilter(
        method="filter_by_upcoming_with_leeway", field_name="time"
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
            return qs.filter(**{name + "__gte": timezone.now()})
        return qs

    def filter_by_upcoming_with_leeway(self, qs, name, value):
        if value:
            return qs.filter(
                **{
                    name
                    + "__gte": timezone.now()
                    - timedelta(
                        minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY
                    )
                }
            )
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
