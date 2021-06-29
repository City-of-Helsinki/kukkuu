import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from projects.models import Project

from children.factories import ChildFactory
from venues.models import Venue

from ..factories import EventFactory, OccurrenceFactory
from ..models import Enrolment, Event, Occurrence

User = get_user_model()


@pytest.mark.django_db
def test_event_creation():
    EventFactory(project=Project.objects.get_or_create(year=2020)[0])

    assert Event.objects.count() == 1


@pytest.mark.django_db
def test_occurrence_creation(event, venue):
    OccurrenceFactory(event=event, venue=venue)

    assert Occurrence.objects.count() == 1
    assert Event.objects.count() == 1
    assert Venue.objects.count() == 1


@pytest.mark.django_db
def test_enrolment_creation(occurrence, project):
    child = ChildFactory(project=project)
    occurrence.children.add(child)
    assert occurrence.children.count() == 1
    assert child.occurrences.count() == 1
    assert Enrolment.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("event_published", [False, True])
def test_occurrence_clean_ticket_system_url(event_published):
    occurrence = OccurrenceFactory.build(
        event__ticket_system=Event.TICKETMASTER,
        event__published_at=now() if event_published else None,
    )

    if event_published:
        with pytest.raises(ValidationError) as ei:
            occurrence.clean()
        assert ei.value.code == "TICKET_SYSTEM_URL_MISSING_ERROR"
    else:
        occurrence.clean()
