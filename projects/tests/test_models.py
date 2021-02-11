import pytest

from children.factories import ChildFactory
from events.factories import EventFactory
from venues.factories import VenueFactory


@pytest.mark.django_db
def test_project_creation(project):
    ChildFactory(project=project)
    EventFactory(project=project)
    VenueFactory(project=project)
    assert project.events.count() == 1
    assert project.venues.count() == 1
