from datetime import datetime, time

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db.models import Exists, OuterRef, Prefetch, Q, Subquery
from django.db.models.functions import Coalesce, ExtractYear
from django.utils import timezone
from django.utils.timezone import make_aware

from children.models import Child
from common.utils import get_node_id_from_global_id
from events.consts import MIN_SEATS_PER_ENROLMENT
from events.models import Event, EventGroup, Occurrence, TicketSystemPassword
from languages.models import Language
from languages.schema import LanguageNode
from tags.models import Accessibility
from tags.schema import AccessibilityNode


class EventSearchService:
    """Service class for child-scoped event search filtering and queryset building."""

    @staticmethod
    def get_search_child(user, raw_child_id: str) -> Child | None:
        """Fetch and prefetch the Child instance specified by child_id."""
        node_id = get_node_id_from_global_id(raw_child_id or "", "ChildNode")
        if not node_id:
            return None
        try:
            return (
                Child.objects.user_can_view(user)
                .select_related("project")
                .prefetch_related(
                    "occurrences__event",
                    "ticket_system_passwords__event",
                )
                .get(id=node_id)
            )
        except (Child.DoesNotExist, ValidationError, ValueError):
            return None

    @staticmethod
    def get_base_queryset(qs, *, child: Child, user, now):
        """
        Build the common base search query for a child.

        Applies project scoping, published/upcoming constraints, event group
        visibility, prefetching of occurrences with capacities, annotations for
        sorting and ticket availability, and default chronological ordering.
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
            .upcoming(now=now)
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
                    queryset=Occurrence.objects.user_can_view(user)
                    .upcoming(now=now)
                    .with_remaining_capacity()
                    .with_enrolment_count()
                    .order_by("time")
                    .select_related("event", "event__project", "venue")
                    .prefetch_related(
                        Prefetch(
                            "venue__translations",
                            queryset=VenueTranslation.objects.order_by("language_code"),
                        ),
                        Prefetch(
                            "accessibilities",
                            queryset=AccessibilityNode.get_queryset(
                                Accessibility.objects.all(), None
                            ),
                        ),
                        Prefetch(
                            "languages",
                            queryset=LanguageNode.get_queryset(
                                Language.objects.all(), None
                            ),
                        ),
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

    @staticmethod
    def filter_family_only(qs):
        """Filter events to only those configured for family attendance."""
        return qs.filter(participants_per_invite=Event.FAMILY)

    @staticmethod
    def filter_theme_paths(qs, theme_paths: list[str]):
        """Filter events tagged with any of the specified theme path slugs."""
        return qs.filter(
            Exists(
                Event.theme_paths.through.objects.filter(
                    event_id=OuterRef("pk"),
                    theme_path_id__in=theme_paths,
                )
            )
        )

    @staticmethod
    def get_matching_occurrences_qs(
        now, *, start_date=None, languages=None, accessibilities=None
    ):
        """
        Build an upcoming occurrences subquery matching start date, languages,
        and accessibilities.
        """
        occ_qs = Occurrence.objects.filter(event=OuterRef("pk"), time__gte=now)
        if start_date:
            start_dt = make_aware(datetime.combine(start_date, time.min))
            occ_qs = occ_qs.filter(time__gte=start_dt)
        if languages:
            occ_qs = occ_qs.in_any_language(languages)
        if accessibilities:
            occ_qs = occ_qs.with_any_accessibility(accessibilities)
        return occ_qs

    @staticmethod
    def filter_has_free_spots(qs, occ_qs):
        """
        Filter events to those that have free space.

        - Internal ticket system events (`Event.INTERNAL`) must have at least one
          upcoming occurrence in `occ_qs` with remaining seat capacity >=
          `MIN_SEATS_PER_ENROLMENT` (2 seats).
        - External ticket system events (Ticketmaster, Lippupiste, Tixly) must
          have at least one unassigned `TicketSystemPassword` and at least one
          matching occurrence in `occ_qs`.
        """
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

    @classmethod
    def filter_occurrences(
        cls,
        qs,
        now,
        *,
        start_date=None,
        languages: list[str] | None = None,
        accessibilities: list[str] | None = None,
        has_free_spots: bool = False,
    ):
        """Filter events by matching upcoming occurrences and optional free capacity."""
        if not (start_date or languages or accessibilities or has_free_spots):
            return qs

        occ_qs = cls.get_matching_occurrences_qs(
            now,
            start_date=start_date,
            languages=languages,
            accessibilities=accessibilities,
        )
        if has_free_spots:
            return cls.filter_has_free_spots(qs, occ_qs)
        return qs.filter(Exists(occ_qs))

    @classmethod
    def search(
        cls,
        qs,
        *,
        child: Child,
        user,
        family_only: bool = False,
        theme_paths: list[str] | None = None,
        start_date=None,
        languages: list[str] | None = None,
        accessibilities: list[str] | None = None,
        has_free_spots: bool = False,
        now=None,
    ):
        """Filter, annotate, and order events suitable for the given child."""
        now = now or timezone.now()
        qs = cls.get_base_queryset(qs, child=child, user=user, now=now)

        if family_only:
            qs = cls.filter_family_only(qs)

        cleaned_theme_paths = list(
            filter(None, (v.strip().lower() for v in theme_paths or () if v))
        )
        if cleaned_theme_paths:
            qs = cls.filter_theme_paths(qs, cleaned_theme_paths)

        return cls.filter_occurrences(
            qs,
            now,
            start_date=start_date,
            languages=list(
                filter(None, (v.strip().lower() for v in languages or () if v))
            ),
            accessibilities=list(
                filter(None, (v.strip().lower() for v in accessibilities or () if v))
            ),
            has_free_spots=has_free_spots,
        )
