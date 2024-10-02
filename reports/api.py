from django.db.models import Prefetch
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_serializer,
    extend_schema_view,
    OpenApiExample,
)
from rest_framework import mixins, viewsets

from children.models import Child
from common.utils import strtobool
from languages.models import Language
from reports.serializers import ChildSerializer


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
