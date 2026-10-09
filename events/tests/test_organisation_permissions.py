import pytest
from django.conf import settings
from graphql_relay import to_global_id

from children.factories import ChildWithGuardianFactory
from events.factories import EnrolmentFactory, EventFactory, OccurrenceFactory
from events.tests.queries import EVENT_QUERY, EVENTS_QUERY, OCCURRENCE_QUERY
from organisations.factories import OrganisationFactory
from organisations.models import Organisation


@pytest.mark.django_db
def test_user_cannot_administer_event_from_other_organisation(
    project_user_api_client, project, event
):
    # The project_user_api_client belongs to "Default Test Organisation" by default
    # The event also belongs to "Default Test Organisation" by default.
    # Let's move the event to another organisation.
    other_org = Organisation.objects.create(name="Other Org")
    event.organisation = other_org
    event.save()

    # User should NOT be able to administer it
    assert not event.can_user_administer(project_user_api_client.user)


@pytest.mark.django_db
def test_system_admin_can_administer_any_event(project_user_api_client, project, event):
    other_org = Organisation.objects.create(name="Other Org")
    event.organisation = other_org
    event.save()

    # User is not a system admin by default.
    assert not event.can_user_administer(project_user_api_client.user)

    # Make user a system admin
    system_org, _ = Organisation.objects.get_or_create(
        name=settings.KUKKUU_DEFAULT_ORGANISATION_NAME
    )
    project_user_api_client.user.organisations.add(system_org)

    assert event.can_user_administer(project_user_api_client.user)


@pytest.mark.django_db
def test_cannot_view_unpublished_event_from_other_organisation(
    project_user_api_client, project, venue
):
    other_org = OrganisationFactory(name="Other Organisation")
    other_event = EventFactory(
        project=project,
        organisation=other_org,
        published_at=None,
        name="Unpublished Other Org Event",
    )
    OccurrenceFactory(event=other_event, venue=venue)

    # In events connection: should not be returned, no errors
    executed = project_user_api_client.execute(EVENTS_QUERY)
    assert executed.get("errors") is None
    event_ids = [edge["node"]["name"] for edge in executed["data"]["events"]["edges"]]
    assert "Unpublished Other Org Event" not in event_ids

    # Querying single node: should return null, no errors
    variables = {"id": to_global_id("EventNode", other_event.id)}
    executed_single = project_user_api_client.execute(EVENT_QUERY, variables=variables)
    assert executed_single.get("errors") is None
    assert executed_single["data"]["event"] is None


@pytest.mark.django_db
def test_public_user_cannot_view_unpublished_event(user_api_client, project, venue):
    unpublished_event = EventFactory(
        project=project,
        published_at=None,
        name="Unpublished Event",
    )
    OccurrenceFactory(event=unpublished_event, venue=venue)

    # In events connection: should not be returned, no errors
    executed = user_api_client.execute(EVENTS_QUERY)
    assert executed.get("errors") is None
    event_ids = [edge["node"]["name"] for edge in executed["data"]["events"]["edges"]]
    assert "Unpublished Event" not in event_ids

    # Querying single node: should return null, no errors
    variables = {"id": to_global_id("EventNode", unpublished_event.id)}
    executed_single = user_api_client.execute(EVENT_QUERY, variables=variables)
    assert executed_single.get("errors") is None
    assert executed_single["data"]["event"] is None


@pytest.mark.django_db
def test_published_event_from_other_organisation_is_viewable(
    project_user_api_client, user_api_client, project, venue
):
    other_org = OrganisationFactory(name="Other Organisation")
    published_event = EventFactory(
        project=project,
        organisation=other_org,
        published_at="2020-01-01T00:00:00Z",
        name="Published Other Org Event",
    )
    OccurrenceFactory(event=published_event, venue=venue)
    variables = {"id": to_global_id("EventNode", published_event.id)}

    # Admin from other org can view published event, with no errors
    executed_admin = project_user_api_client.execute(EVENT_QUERY, variables=variables)
    assert executed_admin.get("errors") is None
    assert executed_admin["data"]["event"] is not None
    assert executed_admin["data"]["event"]["name"] == "Published Other Org Event"

    # Normal user can view published event, with no errors
    executed_user = user_api_client.execute(EVENT_QUERY, variables=variables)
    assert executed_user.get("errors") is None
    assert executed_user["data"]["event"] is not None
    assert executed_user["data"]["event"]["name"] == "Published Other Org Event"


@pytest.mark.django_db
def test_admin_cannot_view_enrolments_from_other_organisation(
    project_user_api_client, project, venue
):
    other_org = OrganisationFactory(name="Other Organisation")
    published_event = EventFactory(
        project=project,
        organisation=other_org,
        published_at="2020-01-01T00:00:00Z",
    )
    occurrence = OccurrenceFactory(event=published_event, venue=venue)
    child = ChildWithGuardianFactory(project=project)
    EnrolmentFactory(child=child, occurrence=occurrence)

    variables = {"id": to_global_id("OccurrenceNode", occurrence.id)}
    executed = project_user_api_client.execute(OCCURRENCE_QUERY, variables=variables)
    assert executed.get("errors") is None
    # Enrolments are isolated to the event's organisation
    assert executed["data"]["occurrence"]["enrolments"]["edges"] == []
