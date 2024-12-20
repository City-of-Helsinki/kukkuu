from django.db.models import Prefetch
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
    extend_schema_serializer,
    extend_schema_view,
)
from rest_framework import mixins, viewsets

from children.models import Child
from common.utils import strtobool
from events.models import Event, EventGroup, Occurrence
from languages.models import Language
from reports.serializers import (
    ChildSerializer,
    EventGroupSerializer,
    EventSerializer,
    VenueSerializer,
)
from venues.models import Venue


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Example 1",
            value=[
                {
                    "registration_date": "2021-02-18",
                    "birthyear": 2021,
                    "contact_language": "fin",
                    "languages_spoken_at_home": ["fin", "nor", "__OTHER__"],
                },
                {
                    "registration_date": "2021-03-18",
                    "birthyear": 2020,
                    "contact_language": "eng",
                    "languages_spoken_at_home": [],
                },
            ],
            response_only=True,
        ),
    ]
)
@extend_schema_view(list=extend_schema(description="Get all children data."))
class ChildViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        Child.objects.exclude(guardians=None)
        .prefetch_related(
            Prefetch(
                "guardians__languages_spoken_at_home",
                queryset=Language.objects.order_by("alpha_3_code"),
                to_attr="prefetched_languages_spoken_at_home",
            ),
        )
        .prefetch_related("guardians")
        .prefetch_related("guardians__user")
        .order_by("name")
    )
    serializer_class = ChildSerializer

    def get_queryset(self):
        filters = {}
        if is_obsolete := self.request.query_params.get("is_obsolete"):  # type: ignore
            try:
                filters["guardians__user__is_obsolete"] = bool(strtobool(is_obsolete))
            except ValueError:
                pass
        return super().get_queryset().filter(**filters)


@extend_schema_view(list=extend_schema(description="Get all events report data."))
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Event.objects.prefetch_related(
            Prefetch(
                "occurrences",
                queryset=Occurrence.objects.with_enrolment_count()
                .with_attended_enrolment_count()
                .with_free_spot_notification_subscription_count()
                .select_related("venue"),
            )
        )
        .select_related("event_group")
        .select_related("project")
    )
    serializer_class = EventSerializer


@extend_schema_view(list=extend_schema(description="Get all event groups."))
class EventGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        EventGroup.objects.prefetch_related("translations")
        .prefetch_related(
            Prefetch(
                "events__occurrences",
                queryset=Occurrence.objects.with_enrolment_count()
                .with_attended_enrolment_count()
                .with_free_spot_notification_subscription_count()
                .select_related("venue"),
            )
        )
        .select_related("project")
    )
    serializer_class = EventGroupSerializer


@extend_schema_view(list=extend_schema(description="Get all venues."))
class VenueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Venue.objects.prefetch_related("translations").select_related("project")
    serializer_class = VenueSerializer
