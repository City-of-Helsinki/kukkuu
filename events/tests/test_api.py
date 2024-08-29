from copy import deepcopy
from datetime import datetime, timedelta
from typing import Dict

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import activate
from freezegun import freeze_time
from graphql_relay import to_global_id
from parler.utils.context import switch_language

from children.factories import ChildWithGuardianFactory
from common.tests.utils import assert_match_error_code, assert_permission_denied
from common.utils import get_global_id
from events.factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    OccurrenceFactory,
    TicketSystemPasswordFactory,
)
from events.models import Enrolment, Event, EventGroup, Occurrence, TicketSystemPassword
from events.tests.mutations import (
    ADD_EVENT_GROUP_MUTATION,
    ADD_EVENT_MUTATION,
    ADD_OCCURRENCE_MUTATION,
    ADD_TICKETMASTER_EVENT_MUTATION,
    ASSIGN_TICKET_SYSTEM_PASSWORD_MUTATION,
    DELETE_EVENT_GROUP_MUTATION,
    DELETE_EVENT_MUTATION,
    DELETE_OCCURRENCE_MUTATION,
    ENROL_OCCURRENCE_MUTATION,
    IMPORT_TICKET_SYSTEM_PASSWORDS_MUTATION,
    PUBLISH_EVENT_GROUP_MUTATION,
    PUBLISH_EVENT_MUTATION,
    SET_ENROLMENT_ATTENDANCE_MUTATION,
    UNENROL_OCCURRENCE_MUTATION,
    UPDATE_EVENT_GROUP_MUTATION,
    UPDATE_EVENT_MUTATION,
    UPDATE_OCCURRENCE_MUTATION,
    UPDATE_TICKETMASTER_EVENT_MUTATION,
)
from events.tests.queries import (
    CAN_CHILD_ENROLL_EVENT_QUERY,
    EVENT_GROUP_EVENTS_FILTER_QUERY,
    EVENT_GROUP_QUERY,
    EVENT_QUERY,
    EVENT_TICKET_SYSTEM_PASSWORD_COUNTS_QUERY,
    EVENT_TICKET_SYSTEM_PASSWORD_QUERY,
    EVENTS_AND_EVENT_GROUPS_SIMPLE_QUERY,
    EVENTS_FILTER_QUERY,
    EVENTS_QUERY,
    GET_ENROLMENT_REFERENCE_ID_QUERY,
    OCCURRENCE_QUERY,
    OCCURRENCE_TICKET_SYSTEM_QUERY,
    OCCURRENCES_COUNTS_QUERY_TEMPLATE,
    OCCURRENCES_FILTER_QUERY,
    OCCURRENCES_QUERY,
    VERIFY_TICKET_QUERY,
)
from events.ticket_service import check_ticket_validity
from kukkuu.consts import (
    CHILD_ALREADY_JOINED_EVENT_ERROR,
    DATA_VALIDATION_ERROR,
    EVENT_ALREADY_PUBLISHED_ERROR,
    EVENT_GROUP_ALREADY_PUBLISHED_ERROR,
    EVENT_GROUP_NOT_READY_FOR_PUBLISHING_ERROR,
    EVENT_NOT_PUBLISHED_ERROR,
    GENERAL_ERROR,
    INELIGIBLE_OCCURRENCE_ENROLMENT,
    MISSING_DEFAULT_TRANSLATION_ERROR,
    NO_FREE_TICKET_SYSTEM_PASSWORDS_ERROR,
    OBJECT_DOES_NOT_EXIST_ERROR,
    OCCURRENCE_IS_FULL_ERROR,
    OCCURRENCE_MISMATCH_ERROR,
    PAST_ENROLMENT_ERROR,
    PAST_OCCURRENCE_ERROR,
    PERMISSION_DENIED_ERROR,
    SINGLE_EVENTS_DISALLOWED_ERROR,
    TICKET_SYSTEM_PASSWORD_ALREADY_ASSIGNED_ERROR,
    TICKET_SYSTEM_PASSWORD_NOTHING_TO_IMPORT_ERROR,
    TICKET_SYSTEM_URL_MISSING_ERROR,
)
from kukkuu.exceptions import EnrolmentReferenceIdDoesNotExist
from kukkuu.views import SentryGraphQLView
from projects.factories import ProjectFactory
from projects.models import Project
from subscriptions.factories import FreeSpotNotificationSubscriptionFactory
from users.factories import GuardianFactory, UserFactory
from venues.factories import VenueFactory


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


ADD_EVENT_VARIABLES = {
    "input": {
        "translations": [
            {
                "name": "Event test",
                "shortDescription": "Short desc",
                "description": "desc",
                "imageAltText": "Image alt text",
                "languageCode": "FI",
            }
        ],
        "duration": 1000,
        "participantsPerInvite": "FAMILY",
        "capacityPerOccurrence": 30,
        "projectId": "",
    }
}


UPDATE_EVENT_VARIABLES = {
    "input": {
        "id": "",
        "translations": [
            {
                "name": "Event test in suomi",
                "shortDescription": "Short desc",
                "description": "desc",
                "imageAltText": "Image alt text",
                "languageCode": "FI",
            },
            {
                "name": "Event test in swedish",
                "shortDescription": "Short desc",
                "description": "desc",
                "imageAltText": "Image alt text",
                "languageCode": "SV",
            },
        ],
        "duration": 1000,
        "participantsPerInvite": "FAMILY",
        "capacityPerOccurrence": 30,
    }
}


PUBLISH_EVENT_VARIABLES = {"input": {"id": ""}}

ADD_OCCURRENCE_VARIABLES = {
    "input": {"eventId": "", "venueId": "", "time": "1986-12-12T16:40:48+00:00"}
}


UPDATE_OCCURRENCE_VARIABLES = {
    "input": {
        "id": "",
        "eventId": "",
        "venueId": "",
        "time": "1986-12-12T16:40:48+00:00",
        "occurrenceLanguage": "SV",
        "capacityOverride": 5,
    }
}


ENROL_OCCURRENCE_VARIABLES = {"input": {"occurrenceId": "", "childId": ""}}


UNENROL_OCCURRENCE_VARIABLES = {"input": {"occurrenceId": "", "childId": ""}}


def test_events_query_unauthenticated(api_client):
    executed = api_client.execute(EVENTS_QUERY)

    assert_permission_denied(executed)


def test_events_query_normal_user(snapshot, user_api_client, event, venue):
    OccurrenceFactory(event=event, venue=venue)
    executed = user_api_client.execute(EVENTS_QUERY)

    snapshot.assert_match(executed)


def test_events_query_project_user(
    snapshot, project_user_api_client, event, unpublished_event, venue, another_project
):
    OccurrenceFactory(event=event, venue=venue)
    OccurrenceFactory(event=unpublished_event, venue=venue)
    # unpublished event from another project, should not be returned
    OccurrenceFactory(event=EventFactory(project=another_project), venue=venue)

    executed = project_user_api_client.execute(EVENTS_QUERY)

    snapshot.assert_match(executed)


def test_event_query_unauthenticated(api_client, event):
    variables = {"id": to_global_id("EventNode", event.id)}
    executed = api_client.execute(EVENT_QUERY, variables=variables)

    assert_permission_denied(executed)


def test_event_query_normal_user(snapshot, user_api_client, event, venue):
    OccurrenceFactory(event=event, venue=venue)
    variables = {"id": to_global_id("EventNode", event.id)}
    executed = user_api_client.execute(EVENT_QUERY, variables=variables)

    snapshot.assert_match(executed)


@pytest.mark.parametrize("enrolment_in_future", [True, False])
def test_event_query_can_child_enroll(
    guardian_api_client,
    child_with_user_guardian,
    future,
    past,
    enrolment_in_future,
):
    """Enrolment shouldn't be allowed since child has enrolled to a different event
    in the same event group.
    """
    event_group = EventGroupFactory(
        name="Event group with one of two events enrolled", published_at=now()
    )
    unenrolled_occurrence = OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__event_group=event_group,
    )
    enrolled_occurrence = OccurrenceFactory(
        time=future if enrolment_in_future else past,
        event__published_at=now() if enrolment_in_future else past,
        event__event_group=event_group,
    )
    EnrolmentFactory(child=child_with_user_guardian, occurrence=enrolled_occurrence)

    variables = {
        "id": to_global_id("EventNode", unenrolled_occurrence.event.id),
        "childId": get_global_id(child_with_user_guardian),
    }

    executed = guardian_api_client.execute(
        CAN_CHILD_ENROLL_EVENT_QUERY, variables=variables
    )

    assert executed["data"]["event"]["canChildEnroll"] is False


def test_occurrences_query_unauthenticated(api_client):
    executed = api_client.execute(OCCURRENCES_QUERY)

    assert_permission_denied(executed)


def test_occurrences_query_normal_user(
    snapshot, user_api_client, occurrence, unpublished_occurrence
):
    executed = user_api_client.execute(OCCURRENCES_QUERY)

    snapshot.assert_match(executed)


def test_occurrences_query_project_user(
    snapshot, project_user_api_client, occurrence, unpublished_occurrence
):
    executed = project_user_api_client.execute(OCCURRENCES_QUERY)

    snapshot.assert_match(executed)


NON_PUBLIC_COUNTS = [
    "attendedEnrolmentCount",
    "freeSpotNotificationSubscriptionCount",
]


@pytest.mark.parametrize("count_field", NON_PUBLIC_COUNTS)
def test_occurrences_query_counts_normal_user(user_api_client, occurrence, count_field):
    FreeSpotNotificationSubscriptionFactory(occurrence=occurrence)
    EnrolmentFactory(occurrence=occurrence)
    EnrolmentFactory(occurrence=occurrence, attended=True)

    executed = user_api_client.execute(
        OCCURRENCES_COUNTS_QUERY_TEMPLATE % {"occurrence_fields": count_field}
    )

    assert_permission_denied(executed)


def test_occurrences_query_counts_project_user(project_user_api_client, occurrence):
    FreeSpotNotificationSubscriptionFactory(occurrence=occurrence)
    EnrolmentFactory(occurrence=occurrence)
    EnrolmentFactory(occurrence=occurrence, attended=True)

    executed = project_user_api_client.execute(
        OCCURRENCES_COUNTS_QUERY_TEMPLATE
        % {"occurrence_fields": "\n".join(NON_PUBLIC_COUNTS)}
    )

    data = executed["data"]["occurrences"]["edges"][0]["node"]
    assert data["enrolmentCount"] == 2
    assert data["attendedEnrolmentCount"] == 1
    assert data["freeSpotNotificationSubscriptionCount"] == 1


def test_occurrence_query_unauthenticated(api_client, occurrence):
    variables = {"id": to_global_id("OccurrenceNode", occurrence.id)}
    executed = api_client.execute(OCCURRENCE_QUERY, variables=variables)

    assert_permission_denied(executed)


def test_occurrence_query_normal_user(snapshot, user_api_client, occurrence):
    variables = {"id": to_global_id("OccurrenceNode", occurrence.id)}
    executed = user_api_client.execute(OCCURRENCE_QUERY, variables=variables)

    snapshot.assert_match(executed)


def test_add_event_permission_denied(api_client, user_api_client):
    executed = api_client.execute(ADD_EVENT_MUTATION, variables=ADD_EVENT_VARIABLES)
    assert_permission_denied(executed)

    executed = user_api_client.execute(
        ADD_EVENT_MUTATION, variables=ADD_EVENT_VARIABLES
    )
    assert_permission_denied(executed)


def test_add_event_project_user(
    snapshot, project_user_api_client, project, event_group
):
    variables = deepcopy(ADD_EVENT_VARIABLES)
    variables["input"]["projectId"] = to_global_id("ProjectNode", project.id)
    variables["input"]["eventGroupId"] = to_global_id("EventGroupNode", event_group.id)
    executed = project_user_api_client.execute(ADD_EVENT_MUTATION, variables=variables)
    snapshot.assert_match(executed)


def test_add_internal_ticket_system_event_capacity_required(
    project_user_api_client, project
):
    variables = deepcopy(ADD_EVENT_VARIABLES)
    variables["input"]["projectId"] = to_global_id("ProjectNode", project.id)
    variables["input"].pop("capacityPerOccurrence")

    executed = project_user_api_client.execute(ADD_EVENT_MUTATION, variables=variables)

    assert_match_error_code(executed, DATA_VALIDATION_ERROR)
    assert "Capacity" in str(executed)


def test_add_ticketmaster_event(snapshot, project_user_api_client, project):
    variables = deepcopy(ADD_EVENT_VARIABLES)
    variables["input"]["projectId"] = get_global_id(project)
    variables["input"]["ticketSystem"] = {
        "type": "TICKETMASTER",
        "url": "https://example.com",
        "endTime": "2020-02-02T02:02:02Z",
    }
    variables["input"].pop("capacityPerOccurrence")

    executed = project_user_api_client.execute(
        ADD_TICKETMASTER_EVENT_MUTATION, variables=variables
    )

    snapshot.assert_match(executed)


def test_add_occurrence_permission_denied(unauthorized_user_api_client, event, venue):
    occurrence_variables = deepcopy(ADD_OCCURRENCE_VARIABLES)
    occurrence_variables["input"]["eventId"] = to_global_id("EventNode", event.id)
    occurrence_variables["input"]["venueId"] = to_global_id("VenueNode", venue.id)

    executed = unauthorized_user_api_client.execute(
        ADD_OCCURRENCE_MUTATION, variables=occurrence_variables
    )
    assert_permission_denied(executed)


def test_add_occurrence_project_user(snapshot, project_user_api_client, event, venue):
    occurrence_variables = deepcopy(ADD_OCCURRENCE_VARIABLES)
    occurrence_variables["input"]["eventId"] = to_global_id("EventNode", event.id)
    occurrence_variables["input"]["venueId"] = to_global_id("VenueNode", venue.id)
    executed = project_user_api_client.execute(
        ADD_OCCURRENCE_MUTATION, variables=occurrence_variables
    )
    snapshot.assert_match(executed)


def test_add_occurrence_different_year(project_user_api_client, event, venue):
    """All occurrences have to be within the same calendar year."""
    OccurrenceFactory(time=timezone.now(), venue=venue, event=event)
    occurrence_variables = deepcopy(ADD_OCCURRENCE_VARIABLES)
    occurrence_variables["input"]["eventId"] = to_global_id("EventNode", event.id)
    occurrence_variables["input"]["venueId"] = to_global_id("VenueNode", venue.id)
    occurrence_variables["input"]["time"] = (
        timezone.now() + timedelta(days=365)
    ).isoformat()

    executed = project_user_api_client.execute(
        ADD_OCCURRENCE_MUTATION, variables=occurrence_variables
    )

    assert_match_error_code(executed, OCCURRENCE_MISMATCH_ERROR)


@pytest.mark.parametrize("single_occurrence", [True, False])
def test_update_occurrence_different_year(
    project_user_api_client, occurrence, single_occurrence, snapshot
):
    """All occurrences have to be within the same calendar year."""
    if not single_occurrence:
        OccurrenceFactory(
            time=timezone.now(), venue=occurrence.venue, event=occurrence.event
        )
    occurrence_variables = deepcopy(UPDATE_OCCURRENCE_VARIABLES)
    occurrence_variables["input"]["id"] = to_global_id("OccurrenceNode", occurrence.id)
    occurrence_variables["input"]["eventId"] = to_global_id(
        "EventNode", occurrence.event.id
    )
    occurrence_variables["input"]["venueId"] = to_global_id(
        "VenueNode", occurrence.venue.id
    )
    occurrence_variables["input"]["time"] = (
        timezone.now() + timedelta(days=365)
    ).isoformat()

    executed = project_user_api_client.execute(
        UPDATE_OCCURRENCE_MUTATION, variables=occurrence_variables
    )

    if single_occurrence:
        snapshot.assert_match(executed)
    else:
        assert_match_error_code(executed, OCCURRENCE_MISMATCH_ERROR)


def test_add_occurrence_ticket_system_url(snapshot, project_user_api_client, venue):
    event = EventFactory(ticket_system=Event.TICKETMASTER)
    variables = deepcopy(ADD_OCCURRENCE_VARIABLES)
    variables["input"]["eventId"] = get_global_id(event)
    variables["input"]["venueId"] = get_global_id(venue)
    variables["input"]["ticketSystem"] = {"url": "https://example.com"}

    executed = project_user_api_client.execute(
        ADD_OCCURRENCE_MUTATION, variables=variables
    )

    snapshot.assert_match(executed)


def test_update_occurrence_permission_denied(api_client, user_api_client):
    executed = api_client.execute(
        UPDATE_OCCURRENCE_MUTATION, variables=UPDATE_OCCURRENCE_VARIABLES
    )
    assert_permission_denied(executed)

    executed = user_api_client.execute(
        UPDATE_OCCURRENCE_MUTATION, variables=UPDATE_OCCURRENCE_VARIABLES
    )
    assert_permission_denied(executed)


def test_update_occurrence_project_user(snapshot, project_user_api_client, occurrence):
    occurrence_variables = deepcopy(UPDATE_OCCURRENCE_VARIABLES)
    occurrence_variables["input"]["id"] = to_global_id("OccurrenceNode", occurrence.id)
    occurrence_variables["input"]["eventId"] = to_global_id(
        "EventNode", occurrence.event.id
    )
    occurrence_variables["input"]["venueId"] = to_global_id(
        "VenueNode", occurrence.venue.id
    )
    executed = project_user_api_client.execute(
        UPDATE_OCCURRENCE_MUTATION, variables=occurrence_variables
    )
    snapshot.assert_match(executed)


@pytest.mark.parametrize("nullify_url", (False, True))
@pytest.mark.parametrize("published", (False, True))
def test_update_occurrence_ticket_system_url(
    snapshot, project_user_api_client, nullify_url, published
):
    occurrence = OccurrenceFactory(
        event__ticket_system=Event.TICKETMASTER,
        event__published_at=now() if published else None,
        ticket_system_url="https://original.example.com",
    )
    variables = deepcopy(UPDATE_OCCURRENCE_VARIABLES)
    variables["input"]["id"] = get_global_id(occurrence)
    variables["input"]["eventId"] = get_global_id(occurrence.event)
    variables["input"]["venueId"] = get_global_id(occurrence.venue)
    variables["input"]["ticketSystem"] = (
        {"url": "https://updated.example.com"} if not nullify_url else {"url": ""}
    )

    executed = project_user_api_client.execute(
        UPDATE_OCCURRENCE_MUTATION, variables=variables
    )

    if nullify_url and published:
        assert_match_error_code(executed, TICKET_SYSTEM_URL_MISSING_ERROR)
    else:
        snapshot.assert_match(executed)


def test_delete_occurrence_permission_denied(api_client, user_api_client):
    executed = api_client.execute(
        DELETE_OCCURRENCE_MUTATION, variables={"input": {"id": ""}}
    )
    assert_permission_denied(executed)

    executed = user_api_client.execute(
        DELETE_OCCURRENCE_MUTATION, variables={"input": {"id": ""}}
    )
    assert_permission_denied(executed)


def test_delete_occurrence_project_user(project_user_api_client, occurrence):
    project_user_api_client.execute(
        DELETE_OCCURRENCE_MUTATION,
        variables={"input": {"id": to_global_id("OccurrenceNode", occurrence.id)}},
    )
    assert Occurrence.objects.count() == 0


def test_update_event_permission_denied(api_client, user_api_client):
    executed = api_client.execute(
        UPDATE_EVENT_MUTATION, variables=UPDATE_EVENT_VARIABLES
    )
    assert_permission_denied(executed)

    executed = user_api_client.execute(
        UPDATE_EVENT_MUTATION, variables=UPDATE_EVENT_VARIABLES
    )
    assert_permission_denied(executed)


def test_update_event_project_user(
    snapshot, project_user_api_client, event, event_group
):
    event_variables = deepcopy(UPDATE_EVENT_VARIABLES)
    event_node_id = to_global_id("EventNode", event.id)
    event_group_node_id = to_global_id("EventGroupNode", event_group.id)
    event_variables["input"]["id"] = event_node_id
    event_variables["input"]["eventGroupId"] = event_group_node_id
    executed = project_user_api_client.execute(
        UPDATE_EVENT_MUTATION, variables=event_variables
    )
    assert executed["data"]["updateEvent"]["event"]["id"] == event_node_id
    assert executed["data"]["updateEvent"]["event"]["eventGroup"]["id"] == (
        event_group_node_id
    )
    snapshot.assert_match(executed)


def test_update_event_ready_for_event_group_publishing(
    snapshot, project_user_api_client, event, event_group
):
    event.event_group = event_group
    event.save()
    assert event.event_group.id == event_group.id

    variables = {
        "input": {"id": get_global_id(event), "readyForEventGroupPublishing": True},
    }
    executed = project_user_api_client.execute(
        UPDATE_EVENT_MUTATION, variables=variables
    )
    assert executed["data"]["updateEvent"]["event"]["readyForEventGroupPublishing"]
    snapshot.assert_match(executed)
    # the event group id should be still set
    event.refresh_from_db()
    assert event.event_group.id == event_group.id


def test_update_ticketmaster_event(snapshot, project_user_api_client):
    event = EventFactory(
        published_at=now(),
        ticket_system=Event.TICKETMASTER,
        ticket_system_url="https://original.example.com",
    )
    variables = deepcopy(UPDATE_EVENT_VARIABLES)
    variables["input"]["id"] = get_global_id(event)
    variables["input"]["ticketSystem"] = {
        "url": "https://updated.example.com",
        "endTime": "2020-02-02T02:02:02Z",
    }
    variables["input"].pop("capacityPerOccurrence")

    executed = project_user_api_client.execute(
        UPDATE_TICKETMASTER_EVENT_MUTATION, variables=variables
    )

    snapshot.assert_match(executed)


def test_update_ticketmaster_event_cannot_change_ticket_system(project_user_api_client):
    event = EventFactory(
        published_at=now(),
        ticket_system=Event.TICKETMASTER,
        ticket_system_url="https://original.example.com",
    )
    variables = deepcopy(UPDATE_EVENT_VARIABLES)
    variables["input"]["id"] = get_global_id(event)
    variables["input"]["ticketSystem"] = Event.INTERNAL
    variables["input"].pop("capacityPerOccurrence")

    project_user_api_client.execute(
        UPDATE_TICKETMASTER_EVENT_MUTATION, variables=variables
    )

    event.refresh_from_db()
    assert event.ticket_system == Event.TICKETMASTER


def test_update_ticketmaster_event_cannot_remove_url(project_user_api_client):
    event = EventFactory(
        published_at=now(),
        ticket_system=Event.TICKETMASTER,
        ticket_system_url="https://original.example.com",
    )
    variables = deepcopy(UPDATE_EVENT_VARIABLES)
    variables["input"]["id"] = get_global_id(event)
    variables["input"]["ticketSystem"] = {"url": ""}
    variables["input"].pop("capacityPerOccurrence")

    executed = project_user_api_client.execute(
        UPDATE_TICKETMASTER_EVENT_MUTATION, variables=variables
    )

    assert_match_error_code(executed, DATA_VALIDATION_ERROR)


def test_delete_event_permission_denied(api_client, user_api_client):
    executed = api_client.execute(
        DELETE_EVENT_MUTATION, variables={"input": {"id": ""}}
    )
    assert_permission_denied(executed)

    executed = user_api_client.execute(
        DELETE_EVENT_MUTATION, variables={"input": {"id": ""}}
    )
    assert_permission_denied(executed)


def test_delete_event_project_user(project_user_api_client, event):
    project_user_api_client.execute(
        DELETE_EVENT_MUTATION,
        variables={"input": {"id": to_global_id("EventNode", event.id)}},
    )
    assert Event.objects.count() == 0


def test_update_event_translations(project_user_api_client, event):
    assert event.translations.count() == 1
    event_variables = deepcopy(UPDATE_EVENT_VARIABLES)
    event_variables["input"]["id"] = to_global_id("EventNode", event.id)

    # Test add translation
    new_translation: Dict[str, (list, str)] = {
        "name": "Event name",
        "description": "Event description",
        "shortDescription": "Event short description",
        "languageCode": "EN",
    }
    event_variables["input"]["translations"].append(new_translation)
    project_user_api_client.execute(UPDATE_EVENT_MUTATION, variables=event_variables)
    assert event.has_translation(new_translation["languageCode"].lower())

    # Test invalid translation
    new_translation["languageCode"] = "foo"
    executed = project_user_api_client.execute(
        UPDATE_EVENT_MUTATION, variables=event_variables
    )

    # GraphQL input error for missing/invalid required fields
    assert_match_error_code(executed, GENERAL_ERROR)
    assert "languageCode" in str(executed["errors"])


def test_upload_image_to_event(project_user_api_client, snapshot, project):
    add_event_variables = deepcopy(ADD_EVENT_VARIABLES)
    add_event_variables["input"]["projectId"] = to_global_id("ProjectNode", project.id)
    # noinspection PyTypeChecker
    add_event_variables["input"]["image"] = SimpleUploadedFile(
        "sample.jpg", content=None, content_type="image/jpeg"
    )

    project_user_api_client.execute(ADD_EVENT_MUTATION, variables=add_event_variables)
    assert Event.objects.count() == 1
    event = Event.objects.first()
    assert event.image


def test_publish_event_no_publish_permission(project_user_api_client):
    event = EventFactory()
    variables = deepcopy(PUBLISH_EVENT_VARIABLES)
    variables["input"]["id"] = get_global_id(event)

    executed = project_user_api_client.execute(
        PUBLISH_EVENT_MUTATION, variables=variables
    )

    assert_permission_denied(executed)


def test_publish_event_not_own_project(publisher_api_client, another_project):
    event = EventFactory(project=another_project)
    variables = deepcopy(PUBLISH_EVENT_VARIABLES)
    variables["input"]["id"] = get_global_id(event)

    executed = publisher_api_client.execute(PUBLISH_EVENT_MUTATION, variables=variables)

    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)


def test_publish_event(snapshot, publisher_api_client, unpublished_event):
    assert not unpublished_event.is_published()
    event_variables = deepcopy(PUBLISH_EVENT_VARIABLES)
    event_variables["input"]["id"] = to_global_id("EventNode", unpublished_event.id)
    executed = publisher_api_client.execute(
        PUBLISH_EVENT_MUTATION, variables=event_variables
    )
    snapshot.assert_match(executed)

    executed = publisher_api_client.execute(
        PUBLISH_EVENT_MUTATION, variables=event_variables
    )

    assert_match_error_code(executed, EVENT_ALREADY_PUBLISHED_ERROR)


@pytest.mark.parametrize("url_missing", (True, False))
def test_publish_ticketmaster_event(snapshot, publisher_api_client, url_missing):
    occurrence = OccurrenceFactory(
        ticket_system_url="" if url_missing else "https://example.com",
        event__ticket_system=Event.TICKETMASTER,
    )
    OccurrenceFactory(ticket_system_url="https://example.com", event=occurrence.event)

    event_variables = deepcopy(PUBLISH_EVENT_VARIABLES)
    event_variables["input"]["id"] = get_global_id(occurrence.event)
    executed = publisher_api_client.execute(
        PUBLISH_EVENT_MUTATION, variables=event_variables
    )

    if url_missing:
        assert_match_error_code(executed, TICKET_SYSTEM_URL_MISSING_ERROR)
    else:
        snapshot.assert_match(executed)


def test_event_filter_by_project(
    two_project_user_api_client, project, another_project, snapshot
):
    EventFactory(name="Should be visible", project=project)
    EventFactory(name="Should NOT be visible", project=another_project)
    variables = {"projectId": get_global_id(project)}

    executed = two_project_user_api_client.execute(
        EVENTS_FILTER_QUERY, variables=variables
    )

    snapshot.assert_match(executed)


def test_event_filter_by_upcoming_events(
    guardian_api_client,
    child_with_user_guardian,
    settings,
):
    not_visible = timezone.now() - timedelta(minutes=5)
    future = timezone.now() + timedelta(days=1)
    # No occurrences
    EventFactory(published_at=now())
    OccurrenceFactory.create(
        time=not_visible, event__name="Not visible", event__published_at=not_visible
    )
    OccurrenceFactory.create(
        time=future, event__name="In the future", event__published_at=now()
    )

    executed = guardian_api_client.execute(
        EVENTS_FILTER_QUERY, variables={"upcoming": True}
    )
    events = [event["node"]["name"] for event in executed["data"]["events"]["edges"]]

    assert set(events) == {"In the future"}


def test_enrol_occurrence(
    api_client, guardian_api_client, snapshot, occurrence, child_with_user_guardian
):
    non_authen_executed = api_client.execute(
        ENROL_OCCURRENCE_MUTATION, variables=ENROL_OCCURRENCE_VARIABLES
    )
    assert_permission_denied(non_authen_executed)

    # old enrollment to another event that should not matter
    EnrolmentFactory(child=child_with_user_guardian)

    enrolment_variables = deepcopy(ENROL_OCCURRENCE_VARIABLES)
    enrolment_variables["input"]["occurrenceId"] = to_global_id(
        "OccurrenceNode", occurrence.id
    )
    enrolment_variables["input"]["childId"] = to_global_id(
        "ChildNode", child_with_user_guardian.id
    )

    executed = guardian_api_client.execute(
        ENROL_OCCURRENCE_MUTATION, variables=enrolment_variables
    )
    snapshot.assert_match(executed)


def test_already_enroled_occurrence(
    guardian_api_client, occurrence, child_with_user_guardian
):
    EnrolmentFactory(child=child_with_user_guardian, occurrence=occurrence)

    enrolment_variables = deepcopy(ENROL_OCCURRENCE_VARIABLES)
    enrolment_variables["input"]["occurrenceId"] = to_global_id(
        "OccurrenceNode", occurrence.id
    )
    enrolment_variables["input"]["childId"] = to_global_id(
        "ChildNode", child_with_user_guardian.id
    )

    executed = guardian_api_client.execute(
        ENROL_OCCURRENCE_MUTATION, variables=enrolment_variables
    )

    assert_match_error_code(executed, CHILD_ALREADY_JOINED_EVENT_ERROR)


def test_enrol_event_not_published(guardian_api_client, child_with_user_guardian):
    event = EventFactory()
    occurrence = OccurrenceFactory(event=event, time=timezone.now() + timedelta(days=1))

    enrolment_variables = deepcopy(ENROL_OCCURRENCE_VARIABLES)
    enrolment_variables["input"]["occurrenceId"] = get_global_id(occurrence)
    enrolment_variables["input"]["childId"] = get_global_id(child_with_user_guardian)

    executed = guardian_api_client.execute(
        ENROL_OCCURRENCE_MUTATION, variables=enrolment_variables
    )

    assert_match_error_code(executed, EVENT_NOT_PUBLISHED_ERROR)


def test_already_enrolled_same_event(
    guardian_api_client, occurrence, child_with_user_guardian
):
    another_occurrence = OccurrenceFactory(
        event=occurrence.event, time=timezone.now() + timedelta(days=1)
    )
    EnrolmentFactory(child=child_with_user_guardian, occurrence=another_occurrence)

    enrolment_variables = deepcopy(ENROL_OCCURRENCE_VARIABLES)
    enrolment_variables["input"]["occurrenceId"] = get_global_id(occurrence)
    enrolment_variables["input"]["childId"] = get_global_id(child_with_user_guardian)

    executed = guardian_api_client.execute(
        ENROL_OCCURRENCE_MUTATION, variables=enrolment_variables
    )

    assert_match_error_code(executed, CHILD_ALREADY_JOINED_EVENT_ERROR)


def test_already_enrolled_same_event_group(
    guardian_api_client, child_with_user_guardian, event_group
):
    event_1 = EventFactory(event_group=event_group, published_at=timezone.now())
    event_2 = EventFactory(event_group=event_group, published_at=timezone.now())
    occurrence_1 = OccurrenceFactory(
        event=event_1, time=timezone.now() + timedelta(days=1)
    )
    occurrence_2 = OccurrenceFactory(
        event=event_2, time=timezone.now() + timedelta(days=2)
    )

    EnrolmentFactory(child=child_with_user_guardian, occurrence=occurrence_1)

    enrolment_variables = deepcopy(ENROL_OCCURRENCE_VARIABLES)
    enrolment_variables["input"]["occurrenceId"] = get_global_id(occurrence_2)
    enrolment_variables["input"]["childId"] = get_global_id(child_with_user_guardian)

    executed = guardian_api_client.execute(
        ENROL_OCCURRENCE_MUTATION, variables=enrolment_variables
    )

    assert_match_error_code(executed, CHILD_ALREADY_JOINED_EVENT_ERROR)


def test_enrol_occurrence_not_allowed(
    guardian_api_client, occurrence, child_with_random_guardian
):
    enrolment_variables = deepcopy(ENROL_OCCURRENCE_VARIABLES)
    enrolment_variables["input"]["occurrenceId"] = to_global_id(
        "OccurrenceNode", occurrence.id
    )
    enrolment_variables["input"]["childId"] = to_global_id(
        "ChildNode", child_with_random_guardian.id
    )

    executed = guardian_api_client.execute(
        ENROL_OCCURRENCE_MUTATION, variables=enrolment_variables
    )
    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)


@freeze_time("2020-11-11")
@pytest.mark.parametrize(
    "enrolled_amount,should_raise", [(0, False), (1, False), (2, True), (3, True)]
)
@pytest.mark.parametrize("use_ticket_system_passwords", [True, False])
def test_enrol_limit_reached(
    enrolled_amount,
    should_raise,
    guardian_api_client,
    child_with_user_guardian,
    snapshot,
    use_ticket_system_passwords,
):
    occurrences = OccurrenceFactory.create_batch(
        enrolled_amount + 1,
        time=timezone.now(),
        event__published_at=timezone.now(),
        event__ticket_system=(
            Event.TICKETMASTER if use_ticket_system_passwords else Event.INTERNAL
        ),
    )
    for i in range(enrolled_amount):
        # Previous enrolments have been with TicketSystemPasswords
        if use_ticket_system_passwords:
            TicketSystemPasswordFactory(
                child=child_with_user_guardian, event=occurrences[i].event
            )
        else:
            EnrolmentFactory(child=child_with_user_guardian, occurrence=occurrences[i])
    occurrence = occurrences[-1]
    enrolment_variables = deepcopy(ENROL_OCCURRENCE_VARIABLES)
    enrolment_variables["input"]["occurrenceId"] = to_global_id(
        "OccurrenceNode", occurrence.id
    )
    enrolment_variables["input"]["childId"] = to_global_id(
        "ChildNode", child_with_user_guardian.id
    )

    executed = guardian_api_client.execute(
        ENROL_OCCURRENCE_MUTATION, variables=enrolment_variables
    )

    if should_raise:
        assert_match_error_code(executed, INELIGIBLE_OCCURRENCE_ENROLMENT)
    else:
        snapshot.assert_match(executed)


def test_unenrol_occurrence(
    api_client,
    user_api_client,
    snapshot,
    occurrence,
    project,
    child_with_random_guardian,
):
    non_authen_executed = api_client.execute(
        UNENROL_OCCURRENCE_MUTATION, variables=ENROL_OCCURRENCE_VARIABLES
    )
    assert_permission_denied(non_authen_executed)

    child = ChildWithGuardianFactory(
        relationship__guardian__user=user_api_client.user, project=project
    )
    EnrolmentFactory(occurrence=occurrence, child=child)

    EnrolmentFactory(occurrence=occurrence, child=child_with_random_guardian)
    assert Enrolment.objects.count() == 2
    assert child.occurrences.count() == 1
    assert child_with_random_guardian.occurrences.count() == 1

    unenrolment_variables = deepcopy(ENROL_OCCURRENCE_VARIABLES)
    unenrolment_variables["input"]["occurrenceId"] = to_global_id(
        "OccurrenceNode", occurrence.id
    )
    unenrolment_variables["input"]["childId"] = to_global_id(
        "ChildNode", child_with_random_guardian.id
    )

    executed = user_api_client.execute(
        UNENROL_OCCURRENCE_MUTATION, variables=unenrolment_variables
    )
    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)
    assert Enrolment.objects.count() == 2
    assert child.occurrences.count() == 1
    assert child_with_random_guardian.occurrences.count() == 1

    unenrolment_variables["input"]["childId"] = to_global_id("ChildNode", child.id)
    executed = user_api_client.execute(
        UNENROL_OCCURRENCE_MUTATION, variables=unenrolment_variables
    )
    assert Enrolment.objects.count() == 1
    assert child.occurrences.count() == 0
    assert child_with_random_guardian.occurrences.count() == 1
    snapshot.assert_match(executed)


def test_ticket_not_valid_after_unenrol(user_api_client, occurrence, project):
    child = ChildWithGuardianFactory(
        relationship__guardian__user=user_api_client.user, project=project
    )
    enrolment = EnrolmentFactory(occurrence=occurrence, child=child)
    assert Enrolment.objects.count() == 1
    to_be_invalid_reference_id = enrolment.reference_id

    unenrolment_variables = deepcopy(ENROL_OCCURRENCE_VARIABLES)
    unenrolment_variables["input"]["occurrenceId"] = to_global_id(
        "OccurrenceNode", occurrence.id
    )
    unenrolment_variables["input"]["childId"] = to_global_id("ChildNode", child.id)
    user_api_client.execute(
        UNENROL_OCCURRENCE_MUTATION, variables=unenrolment_variables
    )
    assert Enrolment.objects.count() == 0

    with pytest.raises(EnrolmentReferenceIdDoesNotExist):
        check_ticket_validity(to_be_invalid_reference_id)


def test_cannot_unenrol_from_occurrence_in_past(
    guardian_api_client, child_with_user_guardian, past
):
    enrolment = EnrolmentFactory(occurrence__time=past, child=child_with_user_guardian)

    variables = deepcopy(UNENROL_OCCURRENCE_VARIABLES)
    variables["input"]["occurrenceId"] = get_global_id(enrolment.occurrence)
    variables["input"]["childId"] = get_global_id(child_with_user_guardian)

    executed = guardian_api_client.execute(
        UNENROL_OCCURRENCE_MUTATION, variables=variables
    )

    assert_match_error_code(executed, PAST_ENROLMENT_ERROR)


def test_maximum_enrolment(
    guardian_api_client, occurrence, project, child_with_user_guardian
):
    max_capactity = occurrence.event.capacity_per_occurrence
    children = ChildWithGuardianFactory.create_batch(max_capactity, project=project)
    for child in children:
        EnrolmentFactory(occurrence=occurrence, child=child)

    enrolment_variables = deepcopy(ENROL_OCCURRENCE_VARIABLES)
    enrolment_variables["input"]["occurrenceId"] = to_global_id(
        "OccurrenceNode", occurrence.id
    )
    enrolment_variables["input"]["childId"] = to_global_id(
        "ChildNode", child_with_user_guardian.id
    )

    executed = guardian_api_client.execute(
        ENROL_OCCURRENCE_MUTATION, variables=enrolment_variables
    )

    assert_match_error_code(executed, OCCURRENCE_IS_FULL_ERROR)


def test_invalid_occurrence_enrolment(
    guardian_api_client, event, venue, child_with_user_guardian
):
    occurrence = OccurrenceFactory(
        time=datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.now().tzinfo),
        venue=venue,
        event=event,
    )
    enrolment_variables = deepcopy(ENROL_OCCURRENCE_VARIABLES)
    enrolment_variables["input"]["occurrenceId"] = to_global_id(
        "OccurrenceNode", occurrence.id
    )
    enrolment_variables["input"]["childId"] = to_global_id(
        "ChildNode", child_with_user_guardian.id
    )
    executed = guardian_api_client.execute(
        ENROL_OCCURRENCE_MUTATION, variables=enrolment_variables
    )

    assert_match_error_code(executed, PAST_OCCURRENCE_ERROR)


def test_normal_translation_fields(snapshot, user_api_client, event):
    variables = {"id": to_global_id("EventNode", event.id)}
    for code in settings.PARLER_SUPPORTED_LANGUAGE_CODES:
        new_translation = "{} Translation".format(code)
        with switch_language(event, code):
            event.name = new_translation
            event.save()
        activate(code)
        executed = user_api_client.execute(EVENT_QUERY, variables=variables)
        translation = [
            trans
            for trans in executed["data"]["event"]["translations"]
            if trans["languageCode"] == code.upper()
        ][0]["name"]
        assert executed["data"]["event"]["name"] == translation


def test_occurrences_filter_by_date(user_api_client, snapshot, event, venue):
    OccurrenceFactory(
        time=datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.now().tzinfo),
        event=event,
        venue=venue,
    )
    OccurrenceFactory(
        time=datetime(1970, 1, 2, 0, 0, 0, tzinfo=timezone.now().tzinfo),
        event=event,
        venue=venue,
    )
    variables = {"date": "1970-01-02"}
    executed = user_api_client.execute(OCCURRENCES_FILTER_QUERY, variables=variables)

    assert len(executed["data"]["occurrences"]["edges"]) == 1
    OccurrenceFactory(
        time=datetime(1970, 1, 2, 0, 0, 0, tzinfo=timezone.now().tzinfo),
        event=event,
        venue=venue,
    )
    executed = user_api_client.execute(OCCURRENCES_FILTER_QUERY, variables=variables)
    assert len(executed["data"]["occurrences"]["edges"]) == 2
    snapshot.assert_match(executed)


def test_occurrences_filter_by_time(user_api_client, snapshot, event, venue):
    for i in range(10, 12):
        OccurrenceFactory(
            time=datetime(1970, 1, 1, i, 0, 0, tzinfo=timezone.now().tzinfo),
            event=event,
            venue=venue,
        )
        OccurrenceFactory(
            time=datetime(1970, 1, 2, i + 1, 0, 0, tzinfo=timezone.now().tzinfo),
            event=event,
            venue=venue,
        )
    OccurrenceFactory(
        time=datetime(1970, 1, 1, 13, 0, 0, tzinfo=timezone.now().tzinfo),
        event=event,
        venue=venue,
    )
    variables_1 = {"time": "12:00:00"}
    variables_2 = {"time": "14:00:00+02:00"}
    variables_3 = {"time": "11:00:00+00:00"}

    executed = user_api_client.execute(OCCURRENCES_FILTER_QUERY, variables=variables_1)
    assert len(executed["data"]["occurrences"]["edges"]) == 1
    executed = user_api_client.execute(OCCURRENCES_FILTER_QUERY, variables=variables_2)
    assert len(executed["data"]["occurrences"]["edges"]) == 1
    executed = user_api_client.execute(OCCURRENCES_FILTER_QUERY, variables=variables_3)
    assert len(executed["data"]["occurrences"]["edges"]) == 2
    snapshot.assert_match(executed)


def test_occurrences_filter_by_upcoming(user_api_client, snapshot, event, venue):
    OccurrenceFactory(
        time=datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.now().tzinfo),
        event=event,
        venue=venue,
    )
    OccurrenceFactory(time=timezone.now(), event=event, venue=venue)
    variables = {"upcoming": True}

    executed = user_api_client.execute(OCCURRENCES_FILTER_QUERY, variables=variables)
    assert len(executed["data"]["occurrences"]["edges"]) == 1
    variables = {"upcoming": False}
    executed = user_api_client.execute(OCCURRENCES_FILTER_QUERY, variables=variables)
    assert len(executed["data"]["occurrences"]["edges"]) == 2

    snapshot.assert_match(executed)


@pytest.mark.parametrize("filter_value", (True, False))
def test_occurrences_filter_by_upcoming_with_leeway(
    user_api_client, snapshot, event, venue, filter_value
):
    OccurrenceFactory(
        time=timezone.now()
        - timedelta(minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY + 1),
        event=event,
        venue=venue,
    )
    OccurrenceFactory(
        time=timezone.now()
        - timedelta(minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY - 1),
        event=event,
        venue=venue,
    )

    executed = user_api_client.execute(
        OCCURRENCES_FILTER_QUERY, variables={"upcomingWithLeeway": filter_value}
    )
    snapshot.assert_match(executed)


@pytest.mark.parametrize("filter_value", (True, False))
def test_occurrences_filter_by_upcoming_with_ongoing(
    user_api_client, snapshot, event, venue, filter_value
):
    event.duration = 60
    event.save()
    OccurrenceFactory(
        time=timezone.now()
        - timedelta(minutes=event.duration)
        - timedelta(minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY + 1),
        event=event,
        venue=venue,
    )
    OccurrenceFactory(
        time=timezone.now()
        - timedelta(minutes=event.duration)
        - timedelta(minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY - 1),
        event=event,
        venue=venue,
    )

    executed = user_api_client.execute(
        OCCURRENCES_FILTER_QUERY, variables={"upcomingWithOngoing": filter_value}
    )
    snapshot.assert_match(executed)


def test_occurrences_filter_by_venue(user_api_client, snapshot, event, venue, project):
    occurrences = OccurrenceFactory.create_batch(
        2, venue=VenueFactory(project=project), event=event
    )
    another_occurrences = OccurrenceFactory.create_batch(3, venue=venue, event=event)

    variables = {"venueId": to_global_id("VenueNode", occurrences[0].venue.id)}
    executed = user_api_client.execute(OCCURRENCES_FILTER_QUERY, variables=variables)
    assert len(executed["data"]["occurrences"]["edges"]) == len(occurrences)

    variables = {"venueId": to_global_id("VenueNode", another_occurrences[0].venue.id)}
    executed = user_api_client.execute(OCCURRENCES_FILTER_QUERY, variables=variables)
    assert len(executed["data"]["occurrences"]["edges"]) == len(another_occurrences)

    snapshot.assert_match(executed)


def test_occurrences_filter_by_event(user_api_client, snapshot, event, project):
    OccurrenceFactory.create_batch(
        2, event=event, time=datetime(1970, 1, 1, 12, tzinfo=timezone.now().tzinfo)
    )
    OccurrenceFactory.create_batch(
        3,
        event__project=project,
        time=datetime(1981, 2, 18, 12, tzinfo=timezone.now().tzinfo),
    )
    variables = {"eventId": to_global_id("EventNode", event.id)}

    executed = user_api_client.execute(OCCURRENCES_FILTER_QUERY, variables=variables)

    snapshot.assert_match(executed)


def test_occurrences_filter_by_language(user_api_client, snapshot, event, venue):
    occurrences = OccurrenceFactory.create_batch(2, venue=venue, event=event)
    sv_occurrences = OccurrenceFactory.create_batch(
        2, venue=venue, event=event, occurrence_language="sv"
    )

    variables = {"occurrenceLanguage": "FI"}
    executed = user_api_client.execute(OCCURRENCES_FILTER_QUERY, variables=variables)
    assert len(executed["data"]["occurrences"]["edges"]) == len(occurrences)

    variables = {"occurrenceLanguage": "SV"}
    executed = user_api_client.execute(OCCURRENCES_FILTER_QUERY, variables=variables)
    assert len(executed["data"]["occurrences"]["edges"]) == len(sv_occurrences)

    snapshot.assert_match(executed)


def test_occurrences_filter_by_project(
    two_project_user_api_client, snapshot, project, another_project
):
    OccurrenceFactory(
        event__project=project,
        event__published_at=now(),
        time=datetime(1970, 1, 1, 12, tzinfo=timezone.now().tzinfo),
    )
    OccurrenceFactory(
        event__project=another_project,
        event__published_at=now(),
        time=datetime(1981, 2, 18, 12, tzinfo=timezone.now().tzinfo),
    )
    variables = {"projectId": get_global_id(project)}

    executed = two_project_user_api_client.execute(
        OCCURRENCES_FILTER_QUERY, variables=variables
    )

    snapshot.assert_match(executed)


def test_occurrence_available_capacity_and_enrolment_count(
    user_api_client, snapshot, occurrence, project
):
    max_capacity = occurrence.event.capacity_per_occurrence
    EnrolmentFactory.create_batch(3, occurrence=occurrence, child__project=project)
    variables = {"id": to_global_id("OccurrenceNode", occurrence.id)}
    executed = user_api_client.execute(OCCURRENCE_QUERY, variables=variables)
    assert executed["data"]["occurrence"]["remainingCapacity"] == max_capacity - 3
    assert executed["data"]["occurrence"]["enrolmentCount"] == 3
    e = EnrolmentFactory(occurrence=occurrence, child__project=project)
    executed = user_api_client.execute(OCCURRENCE_QUERY, variables=variables)
    assert executed["data"]["occurrence"]["remainingCapacity"] == max_capacity - 4
    assert executed["data"]["occurrence"]["enrolmentCount"] == 4
    e.delete()
    executed = user_api_client.execute(OCCURRENCE_QUERY, variables=variables)
    assert executed["data"]["occurrence"]["remainingCapacity"] == max_capacity - 3
    assert executed["data"]["occurrence"]["enrolmentCount"] == 3
    snapshot.assert_match(executed)


def test_enrolment_visibility(
    guardian_api_client, snapshot, occurrence, project, child_with_user_guardian
):
    EnrolmentFactory.create_batch(3, occurrence=occurrence, child__project=project)
    EnrolmentFactory(child=child_with_user_guardian, occurrence=occurrence)
    variables = {"id": to_global_id("OccurrenceNode", occurrence.id)}
    executed = guardian_api_client.execute(OCCURRENCE_QUERY, variables=variables)
    assert len(executed["data"]["occurrence"]["enrolments"]["edges"]) == 1
    snapshot.assert_match(executed)


def test_enrolment_visibility_project_user(
    project_user_api_client, snapshot, project, another_project
):
    enrolment = EnrolmentFactory(
        child__name="ME ME ME",
        child__project=project,
        occurrence__event__project=project,
    )
    EnrolmentFactory(
        child__name="NOT me",
        child__project=another_project,
        occurrence__event__project=another_project,
    )
    variables = {"id": get_global_id(enrolment.occurrence)}

    executed = project_user_api_client.execute(
        """
        query Occurrence($id: ID!) {
          occurrence(id: $id){
            enrolments {
              edges {
                node {
                  child {
                    name
                  }
                }
              }
            }
          }
        }
        """,
        variables=variables,
    )

    snapshot.assert_match(executed)


def test_required_translation(project_user_api_client, snapshot, project):
    # Finnish translation required when creating event
    variable = deepcopy(ADD_EVENT_VARIABLES)
    variable["input"]["projectId"] = to_global_id("ProjectNode", project.id)
    variable["input"]["translations"][0]["languageCode"] = "SV"
    executed = project_user_api_client.execute(ADD_EVENT_MUTATION, variables=variable)
    assert_match_error_code(executed, MISSING_DEFAULT_TRANSLATION_ERROR)
    variable["input"]["translations"][0]["languageCode"] = "FI"
    executed = project_user_api_client.execute(ADD_EVENT_MUTATION, variables=variable)
    snapshot.assert_match(executed)

    # Test delete default translation
    event = EventFactory(project=project)
    if not event.has_translation("fi"):
        event.create_translation(language_code="fi", **{"name": "Finnish translation"})
    event_variables = {
        "input": {
            "id": "",
            "translations": [
                {
                    "name": "Event test in swedish",
                    "shortDescription": "Short desc",
                    "description": "desc",
                    "imageAltText": "Image alt text",
                    "languageCode": "SV",
                }
            ],
            "duration": 1000,
            "participantsPerInvite": "FAMILY",
            "capacityPerOccurrence": 30,
        }
    }
    event_variables["input"]["id"] = to_global_id("EventNode", event.id)
    executed = project_user_api_client.execute(
        UPDATE_EVENT_MUTATION, variables=event_variables
    )
    assert_match_error_code(executed, MISSING_DEFAULT_TRANSLATION_ERROR)


def test_update_field_with_null_value(project_user_api_client, project):
    event = EventFactory(project=project)
    # To make sure event has Finnish translation and bypass the language validation
    if not event.has_translation("fi"):
        event.create_translation(language_code="fi", **{"name": "Finnish translation"})
    event_variables = deepcopy(UPDATE_EVENT_VARIABLES)
    event_variables["input"]["id"] = to_global_id("EventNode", event.id)
    # Null value for not-nullable field
    event_variables["input"]["participantsPerInvite"] = None
    executed = project_user_api_client.execute(
        UPDATE_EVENT_MUTATION, variables=event_variables
    )
    assert_match_error_code(executed, DATA_VALIDATION_ERROR)
    assert "cannot be null" in str(executed["errors"])


def test_child_enrol_occurence_from_different_project(
    snapshot, guardian_api_client, child_with_user_guardian, occurrence
):
    next_project = ProjectFactory(year=2021)
    another_occurrence = OccurrenceFactory(
        event__project=next_project,
        event__published_at=timezone.now(),
        venue__project=next_project,
    )
    assert Occurrence.objects.count() == 2
    enrolment_variables = deepcopy(ENROL_OCCURRENCE_VARIABLES)
    enrolment_variables["input"]["occurrenceId"] = to_global_id(
        "OccurrenceNode", occurrence.id
    )
    enrolment_variables["input"]["childId"] = to_global_id(
        "ChildNode", child_with_user_guardian.id
    )

    executed = guardian_api_client.execute(
        ENROL_OCCURRENCE_MUTATION, variables=enrolment_variables
    )
    snapshot.assert_match(executed)
    enrolment_variables["input"]["occurrenceId"] = to_global_id(
        "OccurrenceNode", another_occurrence.id
    )
    enrolment_variables["input"]["childId"] = to_global_id(
        "ChildNode", child_with_user_guardian.id
    )

    executed = guardian_api_client.execute(
        ENROL_OCCURRENCE_MUTATION, variables=enrolment_variables
    )
    assert_match_error_code(executed, INELIGIBLE_OCCURRENCE_ENROLMENT)


@pytest.mark.parametrize(
    "max_query_depth,expected_error_message",
    [
        (3, "'Events' exceeds maximum operation depth of 3."),
        (4, None),
    ],
)
def test_api_query_depth(settings, event, max_query_depth, expected_error_message):
    settings.KUKKUU_QUERY_MAX_DEPTH = max_query_depth
    user = UserFactory(guardian=GuardianFactory())
    request = RequestFactory().post("/graphql")
    request.user = user

    query = """
    query Events {
      events {
        edges {
          node {
            project {
              name
            }
          }
        }
      }
    }
    """

    view = SentryGraphQLView()
    result = view.execute_graphql_request(
        request=request,
        data=None,
        variables=None,
        operation_name="Events",
        query=query,
    )

    assert (result.errors is None) == (expected_error_message is None)
    assert str(expected_error_message) in str(result.errors)


@pytest.mark.parametrize("expected_attended", [True, None])
def test_set_enrolment_attendance(
    snapshot,
    project_user_api_client,
    occurrence,
    child_with_user_guardian,
    expected_attended,
):
    enrolment = EnrolmentFactory(
        occurrence=occurrence,
        child=child_with_user_guardian,
        attended=None if expected_attended else True,
    )
    variables = {
        "input": {
            "enrolmentId": get_global_id(enrolment),
            "attended": expected_attended,
        }
    }

    executed = project_user_api_client.execute(
        SET_ENROLMENT_ATTENDANCE_MUTATION, variables=variables
    )

    snapshot.assert_match(executed)
    enrolment.refresh_from_db()
    assert enrolment.attended == expected_attended


def test_set_enrolment_attendance_another_project_child(
    project_user_api_client,
    occurrence,
    another_project,
):
    another_project_child = ChildWithGuardianFactory(project=another_project)
    enrolment = EnrolmentFactory(
        occurrence=occurrence, child=another_project_child, attended=None
    )
    variables = {"input": {"enrolmentId": get_global_id(enrolment), "attended": True}}

    executed = project_user_api_client.execute(
        SET_ENROLMENT_ATTENDANCE_MUTATION, variables=variables
    )

    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)


@pytest.mark.parametrize(
    "capacity_override, enrolment_count",
    (
        (5, 0),
        (5, 4),
        (5, 5),
        (5, 6),
        (None, 0),
        (None, 9),
        (None, 10),
        (None, 11),
        (0, 0),
    ),
)
def test_occurrence_capacity(
    snapshot, guardian_api_client, project, capacity_override, enrolment_count
):
    occurrence = OccurrenceFactory(
        event__project=project,
        venue__project=project,
        event__published_at=now(),
        event__capacity_per_occurrence=10,
        capacity_override=capacity_override,
    )
    EnrolmentFactory.create_batch(
        enrolment_count, occurrence=occurrence, child__project=project
    )

    executed = guardian_api_client.execute(
        """
            query OccurrenceCapacity($id: ID!) {
              occurrence(id: $id){
                capacity
                capacityOverride
                enrolmentCount
                remainingCapacity
              }
            }
        """,
        variables={"id": get_global_id(occurrence)},
    )

    snapshot.assert_match(executed)


@pytest.mark.parametrize("published", (False, True))
def test_event_group_query_normal_user_and_project_user(
    snapshot, user_api_client, project_user_api_client, published
):
    event_group = EventGroupFactory(published_at=now() if published else None)
    variables = {"id": get_global_id(event_group)}

    executed = user_api_client.execute(EVENT_GROUP_QUERY, variables=variables)
    snapshot.assert_match(executed)

    executed = project_user_api_client.execute(EVENT_GROUP_QUERY, variables=variables)
    snapshot.assert_match(executed)


def test_event_group_query_wrong_project(
    snapshot, project_user_api_client, another_project
):
    event_group = EventGroupFactory(project=another_project)

    executed = project_user_api_client.execute(
        EVENT_GROUP_QUERY, variables={"id": get_global_id(event_group)}
    )

    snapshot.assert_match(executed)


def test_events_and_event_groups_query_normal_user(snapshot, guardian_api_client):
    EventFactory(name="I'M UNPUBLISHED AND SHOULDN'T BE VISIBLE")
    EventFactory(name="Published Event", published_at=now())
    EventGroupFactory(name="I'M UNPUBLISHED AND SHOULD NOT BE VISIBLE")
    EventGroupFactory(name="Published EventGroup", published_at=now())

    executed = guardian_api_client.execute(EVENTS_AND_EVENT_GROUPS_SIMPLE_QUERY)

    snapshot.assert_match(executed)


def test_events_and_event_groups_query_project_user(snapshot, project_user_api_client):
    first_event = EventFactory(name="I should be the first")
    EventFactory(event_group=EventGroupFactory(name="I should be the in the middle"))
    last_event = EventFactory(name="I should be the last")
    Event.objects.filter(pk=first_event.pk).update(
        created_at=now() + timedelta(minutes=1)
    )
    Event.objects.filter(pk=last_event.pk).update(
        created_at=now() - timedelta(minutes=1)
    )

    executed = project_user_api_client.execute(EVENTS_AND_EVENT_GROUPS_SIMPLE_QUERY)

    snapshot.assert_match(executed)


def test_events_and_event_groups_query_project_filtering(
    snapshot,
    project_user_api_client,
    two_project_user_api_client,
    project,
    another_project,
):
    EventGroupFactory(name="The project's EventGroup", project=project)
    EventFactory(name="The project's Event", project=project)
    EventGroupFactory(name="Another project's EventGroup", project=another_project)
    EventFactory(name="Another project's Event", project=another_project)

    executed = project_user_api_client.execute(EVENTS_AND_EVENT_GROUPS_SIMPLE_QUERY)
    snapshot.assert_match(
        executed, name="No filter, no permission to see another project"
    )

    executed = two_project_user_api_client.execute(EVENTS_AND_EVENT_GROUPS_SIMPLE_QUERY)
    snapshot.assert_match(executed, name="No filter, permission to see both projects")

    executed = two_project_user_api_client.execute(
        EVENTS_AND_EVENT_GROUPS_SIMPLE_QUERY,
        variables={"projectId": get_global_id(project)},
    )
    snapshot.assert_match(
        executed, name="First project in filter, permission to see both projects"
    )


@pytest.mark.parametrize("has_event_group", [True, False])
def test_events_and_event_groups_query_upcoming_filter(
    guardian_api_client,
    child_with_user_guardian,
    settings,
    snapshot,
    has_event_group,
):
    not_visible = timezone.now() - timedelta(minutes=5)
    future = timezone.now() + timedelta(days=1)

    # No occurrences
    EventFactory(
        published_at=now(),
        event_group=EventGroupFactory(published_at=now()) if has_event_group else None,
    )
    OccurrenceFactory.create(
        time=not_visible,
        event__name="Not visible",
        event__published_at=not_visible,
        event__event_group=(
            EventGroupFactory(name="Not visible", published_at=not_visible)
            if has_event_group
            else None
        ),
    )
    OccurrenceFactory.create(
        time=future,
        event__name="In the future",
        event__published_at=now(),
        event__event_group=(
            EventGroupFactory(name="In the future", published_at=now())
            if has_event_group
            else None
        ),
    )

    executed = guardian_api_client.execute(
        EVENTS_AND_EVENT_GROUPS_SIMPLE_QUERY, variables={"upcoming": True}
    )

    snapshot.assert_match(executed)


ADD_EVENT_GROUP_VARIABLES = {
    "input": {
        "translations": [
            {
                "name": "Event group test",
                "shortDescription": "Short desc",
                "description": "desc",
                "imageAltText": "Image alt text",
                "languageCode": "FI",
            }
        ],
        "projectId": "",
    }
}


def test_add_event_group_permission_denied(
    api_client, user_api_client, project_user_api_client, project
):
    variables = deepcopy(ADD_EVENT_GROUP_VARIABLES)
    variables["input"]["projectId"] = get_global_id(project)

    executed = api_client.execute(ADD_EVENT_GROUP_MUTATION, variables=variables)
    assert_permission_denied(executed)

    executed = user_api_client.execute(ADD_EVENT_GROUP_MUTATION, variables=variables)
    assert_permission_denied(executed)

    executed = project_user_api_client.execute(
        ADD_EVENT_GROUP_MUTATION, variables=variables
    )
    assert_permission_denied(executed)


def test_add_event_group(snapshot, event_group_manager_api_client, project):
    variables = deepcopy(ADD_EVENT_GROUP_VARIABLES)
    variables["input"]["projectId"] = get_global_id(project)

    executed = event_group_manager_api_client.execute(
        ADD_EVENT_GROUP_MUTATION, variables=variables
    )
    snapshot.assert_match(executed)


UPDATE_EVENT_GROUP_VARIABLES = {
    "input": {
        "id": "",
        "translations": [
            {
                "name": "Event group test in suomi",
                "shortDescription": "Short desc",
                "description": "desc",
                "imageAltText": "Image alt text",
                "languageCode": "FI",
            },
            {
                "name": "Event group test in swedish",
                "shortDescription": "Short desc",
                "description": "desc",
                "imageAltText": "Image alt text",
                "languageCode": "SV",
            },
        ],
    }
}


def test_update_event_group_permission_denied(
    api_client, user_api_client, project_user_api_client, event_group
):
    variables = deepcopy(UPDATE_EVENT_GROUP_VARIABLES)
    variables["input"]["id"] = get_global_id(event_group)

    executed = api_client.execute(UPDATE_EVENT_GROUP_MUTATION, variables=variables)
    assert_permission_denied(executed)

    executed = user_api_client.execute(UPDATE_EVENT_GROUP_MUTATION, variables=variables)
    assert_permission_denied(executed)

    executed = project_user_api_client.execute(
        UPDATE_EVENT_GROUP_MUTATION, variables=variables
    )
    assert_permission_denied(executed)


def test_update_event_group(snapshot, event_group_manager_api_client, event_group):
    variables = deepcopy(UPDATE_EVENT_GROUP_VARIABLES)
    variables["input"]["id"] = get_global_id(event_group)
    executed = event_group_manager_api_client.execute(
        UPDATE_EVENT_GROUP_MUTATION, variables=variables
    )
    snapshot.assert_match(executed)


def test_delete_event_group_permission_denied(
    api_client, user_api_client, project_user_api_client, event_group
):
    variables = {"input": {"id": get_global_id(event_group)}}
    executed = api_client.execute(DELETE_EVENT_GROUP_MUTATION, variables=variables)
    assert_permission_denied(executed)

    executed = user_api_client.execute(DELETE_EVENT_GROUP_MUTATION, variables=variables)
    assert_permission_denied(executed)

    executed = project_user_api_client.execute(
        DELETE_EVENT_GROUP_MUTATION, variables=variables
    )
    assert_permission_denied(executed)


def test_delete_event_group(snapshot, event_group_manager_api_client, event_group):
    executed = event_group_manager_api_client.execute(
        DELETE_EVENT_GROUP_MUTATION,
        variables={"input": {"id": get_global_id(event_group)}},
    )

    snapshot.assert_match(executed)
    assert EventGroup.objects.count() == 0


PUBLISH_EVENT_GROUP_VARIABLES = {"input": {"id": ""}}


def test_publish_event_group_no_publish_permission(project_user_api_client):
    event = EventFactory(event_group=EventGroupFactory())
    variables = deepcopy(PUBLISH_EVENT_GROUP_VARIABLES)
    variables["input"]["id"] = get_global_id(event.event_group)

    executed = project_user_api_client.execute(
        PUBLISH_EVENT_GROUP_MUTATION, variables=variables
    )

    assert_permission_denied(executed)


def test_publish_event_group_not_own_project(publisher_api_client, another_project):
    event = EventFactory(
        project=another_project, event_group=EventGroupFactory(project=another_project)
    )
    variables = deepcopy(PUBLISH_EVENT_GROUP_VARIABLES)
    variables["input"]["id"] = get_global_id(event.event_group)

    executed = publisher_api_client.execute(
        PUBLISH_EVENT_GROUP_MUTATION, variables=variables
    )

    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)


def test_publish_event_group_events_not_ready(publisher_api_client):
    event = EventFactory(event_group=EventGroupFactory())
    EventFactory(event_group=event.event_group, ready_for_event_group_publishing=False)
    variables = deepcopy(PUBLISH_EVENT_GROUP_VARIABLES)
    variables["input"]["id"] = get_global_id(event.event_group)

    executed = publisher_api_client.execute(
        PUBLISH_EVENT_GROUP_MUTATION, variables=variables
    )

    assert_match_error_code(executed, EVENT_GROUP_NOT_READY_FOR_PUBLISHING_ERROR)


def test_publish_event_group(snapshot, publisher_api_client):
    event = EventFactory(
        event_group=EventGroupFactory(), ready_for_event_group_publishing=True
    )
    variables = deepcopy(PUBLISH_EVENT_GROUP_VARIABLES)
    variables["input"]["id"] = get_global_id(event.event_group)

    executed = publisher_api_client.execute(
        PUBLISH_EVENT_GROUP_MUTATION, variables=variables
    )

    snapshot.assert_match(executed)

    event.refresh_from_db()
    assert event.event_group.published_at
    assert event.published_at

    executed = publisher_api_client.execute(
        PUBLISH_EVENT_GROUP_MUTATION, variables=variables
    )

    assert_match_error_code(executed, EVENT_GROUP_ALREADY_PUBLISHED_ERROR)


@pytest.mark.parametrize("event_ready", [True, False])
def test_republish_event_group(snapshot, publisher_api_client, event_ready, past):
    """Event group can be republished if it contains unpublished events which
    are ready for publishing.
    """
    event_group = EventGroupFactory(published_at=past)
    EventFactory(
        event_group=event_group,
        ready_for_event_group_publishing=True,
        published_at=past,
    )
    new_event = EventFactory(
        event_group=event_group,
        ready_for_event_group_publishing=event_ready,
    )

    variables = deepcopy(PUBLISH_EVENT_GROUP_VARIABLES)
    variables["input"]["id"] = get_global_id(event_group)

    executed = publisher_api_client.execute(
        PUBLISH_EVENT_GROUP_MUTATION, variables=variables
    )

    new_event.refresh_from_db()

    if event_ready:
        snapshot.assert_match(executed)
        assert new_event.published_at
    else:
        assert_match_error_code(executed, EVENT_GROUP_NOT_READY_FOR_PUBLISHING_ERROR)
        assert not new_event.published_at


def test_event_group_events_filtering_by_available_for_child_id(
    snapshot, guardian_api_client, user_api_client, event_group, past, future
):
    child_with_guardian = ChildWithGuardianFactory(
        relationship__guardian__user=guardian_api_client.user
    )
    OccurrenceFactory(
        time=past, event__published_at=past, event__event_group=event_group
    )
    OccurrenceFactory(
        time=future,
        event__published_at=past,
        event__name="ME ME ME",
        event__event_group=event_group,
    )

    variables = {
        "id": get_global_id(event_group),
        "availableForChild": get_global_id(child_with_guardian),
    }

    executed = guardian_api_client.execute(
        EVENT_GROUP_EVENTS_FILTER_QUERY, variables=variables
    )
    snapshot.assert_match(executed)

    # filtering by someone else's child should not do anything
    executed = user_api_client.execute(
        EVENT_GROUP_EVENTS_FILTER_QUERY, variables=variables
    )
    snapshot.assert_match(executed)


def test_add_single_event_when_single_events_disallowed(
    project_user_api_client, project
):
    Project.objects.filter(id=project.id).update(single_events_allowed=False)

    variables = deepcopy(ADD_EVENT_VARIABLES)
    variables["input"]["projectId"] = to_global_id("ProjectNode", project.id)
    executed = project_user_api_client.execute(ADD_EVENT_MUTATION, variables=variables)

    assert_match_error_code(executed, SINGLE_EVENTS_DISALLOWED_ERROR)


def test_occurrence_ticket_system(snapshot, guardian_api_client):
    occurrence = OccurrenceFactory(
        ticket_system_url="https://example.com",
        event__ticket_system=Event.TICKETMASTER,
        event__published_at=now(),
    )

    executed = guardian_api_client.execute(
        OCCURRENCE_TICKET_SYSTEM_QUERY, variables={"id": get_global_id(occurrence)}
    )

    snapshot.assert_match(executed)


def test_event_ticket_system_password_own_child_password_exists(
    snapshot, guardian_api_client
):
    event = EventFactory(ticket_system=Event.TICKETMASTER, published_at=now())
    child = ChildWithGuardianFactory(
        relationship__guardian__user=guardian_api_client.user.guardian.user
    )
    existing_password = TicketSystemPasswordFactory(
        event=event, child=child, value="the correct password"
    )

    variables = {"eventId": get_global_id(event), "childId": get_global_id(child)}

    executed = guardian_api_client.execute(
        EVENT_TICKET_SYSTEM_PASSWORD_QUERY,
        variables=variables,
    )

    snapshot.assert_match(executed)
    assert child.ticket_system_passwords.get(event=event) == existing_password


def test_event_ticket_system_password_own_child_no_password(guardian_api_client):
    event = EventFactory(ticket_system=Event.TICKETMASTER, published_at=now())
    child = ChildWithGuardianFactory(
        relationship__guardian__user=guardian_api_client.user.guardian.user
    )

    variables = {"eventId": get_global_id(event), "childId": get_global_id(child)}

    executed = guardian_api_client.execute(
        EVENT_TICKET_SYSTEM_PASSWORD_QUERY,
        variables=variables,
    )

    assert executed["data"]["event"]["ticketSystem"]["childPassword"] is None
    assert not child.ticket_system_passwords.filter(event=event).exists()


def test_event_ticket_system_password_not_own_child(guardian_api_client):
    event = EventFactory(ticket_system=Event.TICKETMASTER, published_at=now())
    another_child = ChildWithGuardianFactory()
    another_childs_password = TicketSystemPasswordFactory(  # noqa: F841
        event=event, child=another_child, value="FATAL LEAK"
    )
    some_free_password = TicketSystemPasswordFactory(event=event)  # noqa: F841

    variables = {
        "eventId": get_global_id(event),
        "childId": get_global_id(another_child),
    }

    executed = guardian_api_client.execute(
        EVENT_TICKET_SYSTEM_PASSWORD_QUERY,
        variables=variables,
    )

    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)


def test_event_ticket_system_password_counts(snapshot, project_user_api_client):
    event = EventFactory(ticket_system=Event.TICKETMASTER, published_at=now())

    # free passwords
    TicketSystemPasswordFactory.create_batch(3, event=event, child=None)

    # used passwords
    TicketSystemPasswordFactory.create_batch(2, event=event, assigned_at=now())

    # another event free passwords, should not affect anything
    TicketSystemPasswordFactory.create_batch(7, child=None)

    # another event used passwords, should not affect anything
    TicketSystemPasswordFactory.create_batch(6, assigned_at=now())

    variables = {"eventId": get_global_id(event)}

    executed = project_user_api_client.execute(
        EVENT_TICKET_SYSTEM_PASSWORD_COUNTS_QUERY,
        variables=variables,
    )

    # expect 3 free passwords and 2 used passwords
    snapshot.assert_match(executed)


def test_event_ticket_system_password_counts_no_permission(guardian_api_client):
    event = EventFactory(ticket_system=Event.TICKETMASTER, published_at=now())
    TicketSystemPasswordFactory.create_batch(3, event=event, child=None)

    variables = {"eventId": get_global_id(event)}

    executed = guardian_api_client.execute(
        EVENT_TICKET_SYSTEM_PASSWORD_COUNTS_QUERY,
        variables=variables,
    )

    assert_match_error_code(executed, PERMISSION_DENIED_ERROR)


def test_import_ticket_system_passwords(snapshot, project_user_api_client):
    """project admins should be able to import a list passwords to an event."""
    event = EventFactory(ticket_system=Event.TICKETMASTER)
    passwords = ["123", "asd", "xyz321"]

    executed = project_user_api_client.execute(
        IMPORT_TICKET_SYSTEM_PASSWORDS_MUTATION,
        variables={"input": {"eventId": get_global_id(event), "passwords": passwords}},
    )
    snapshot.assert_match(executed)
    assert (
        executed["data"]["importTicketSystemPasswords"]["event"]["name"] == event.name
    )
    assert executed["data"]["importTicketSystemPasswords"]["passwords"] == passwords
    assert TicketSystemPassword.objects.count() == len(passwords)


def test_import_ticket_system_passwords_errors_with_integrity_errors(
    snapshot, project_user_api_client
):
    """
    When importing some non-unique passwords,
    the process should continue and
    the given unique passwords should be imported
    and the errors should be listed in the errors field.
    """
    existing_passwords = ["123", "asd", "xyz321"]
    event = EventFactory(ticket_system=Event.TICKETMASTER)
    for password in existing_passwords:
        TicketSystemPasswordFactory(event=event, value=password)

    passwords_imported = (
        ["more", "passwords"] + existing_passwords + ["to", "test", "errors"]
    )

    executed = project_user_api_client.execute(
        IMPORT_TICKET_SYSTEM_PASSWORDS_MUTATION,
        variables={
            "input": {"eventId": get_global_id(event), "passwords": passwords_imported}
        },
    )
    new_passwords = [p for p in passwords_imported if p not in existing_passwords]
    snapshot.assert_match(executed)
    assert (
        executed["data"]["importTicketSystemPasswords"]["event"]["name"] == event.name
    )
    # Passwords should contain only the added passwords
    assert executed["data"]["importTicketSystemPasswords"]["passwords"] == new_passwords
    error_values = [
        e["value"] for e in executed["data"]["importTicketSystemPasswords"]["errors"]
    ]
    assert all([p in error_values for p in existing_passwords])
    assert all([p not in error_values for p in new_passwords])
    assert TicketSystemPassword.objects.count() == len(
        new_passwords + existing_passwords
    )


def test_import_ticket_system_passwords_missing_required_params(
    project_user_api_client,
):
    """Some of the required params are missing"""
    # No passwords
    event = EventFactory(ticket_system=Event.TICKETMASTER)
    executed = project_user_api_client.execute(
        IMPORT_TICKET_SYSTEM_PASSWORDS_MUTATION,
        variables={"input": {"eventId": get_global_id(event), "passwords": None}},
    )
    assert_match_error_code(executed, GENERAL_ERROR)

    # No event id
    executed = project_user_api_client.execute(
        IMPORT_TICKET_SYSTEM_PASSWORDS_MUTATION,
        variables={"input": {"eventId": None, "passwords": ["secret-coupon"]}},
    )
    assert_match_error_code(executed, GENERAL_ERROR)

    # Empty list of passwords
    event = EventFactory(ticket_system=Event.TICKETMASTER)
    executed = project_user_api_client.execute(
        IMPORT_TICKET_SYSTEM_PASSWORDS_MUTATION,
        variables={"input": {"eventId": get_global_id(event), "passwords": []}},
    )
    assert_match_error_code(executed, TICKET_SYSTEM_PASSWORD_NOTHING_TO_IMPORT_ERROR)


def test_import_ticket_system_passwords_event_not_exist(project_user_api_client):
    """The event where the passwords are imported does not exist"""
    event = EventFactory(ticket_system=Event.TICKETMASTER)
    event_id = get_global_id(event)
    event.delete()
    executed = project_user_api_client.execute(
        IMPORT_TICKET_SYSTEM_PASSWORDS_MUTATION,
        variables={"input": {"eventId": event_id, "passwords": ["secret-coupon"]}},
    )
    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)


def test_import_ticket_system_passwords_invalid_permissions(guardian_api_client):
    """
    The user who is importing does not have enough permissions to do the operation.
    Only the project admins should have the permissions.
    """
    event = EventFactory(ticket_system=Event.TICKETMASTER)
    executed = guardian_api_client.execute(
        IMPORT_TICKET_SYSTEM_PASSWORDS_MUTATION,
        variables={
            "input": {"eventId": get_global_id(event), "passwords": ["secret-coupon"]}
        },
    )
    assert_match_error_code(executed, PERMISSION_DENIED_ERROR)


def test_assign_ticket_system_password(snapshot, guardian_api_client):
    event = EventFactory(ticket_system=Event.TICKETMASTER, published_at=now())
    child = ChildWithGuardianFactory(
        relationship__guardian__user=guardian_api_client.user.guardian.user
    )
    someone_elses_password = TicketSystemPasswordFactory(  # noqa: F841
        event=event, value="FATAL LEAK", assigned_at=now()
    )
    free_password = TicketSystemPasswordFactory(
        event=event, child=None, value="the correct password"
    )
    another_free_password = TicketSystemPasswordFactory(  # noqa: F841
        event=event, child=None, value="wrong password"
    )

    variables = {
        "input": {
            "eventId": get_global_id(event),
            "childId": get_global_id(child),
        }
    }

    executed = guardian_api_client.execute(
        ASSIGN_TICKET_SYSTEM_PASSWORD_MUTATION,
        variables=variables,
    )

    snapshot.assert_match(executed)
    assert child.ticket_system_passwords.get(event=event) == free_password

    # second mutation should result in password already assigned error
    executed = guardian_api_client.execute(
        ASSIGN_TICKET_SYSTEM_PASSWORD_MUTATION,
        variables=variables,
    )

    assert_match_error_code(executed, TICKET_SYSTEM_PASSWORD_ALREADY_ASSIGNED_ERROR)


def test_assign_ticket_system_password_no_free_passwords(
    guardian_api_client,
):
    event = EventFactory(ticket_system=Event.TICKETMASTER, published_at=now())
    child = ChildWithGuardianFactory(
        relationship__guardian__user=guardian_api_client.user.guardian.user
    )
    someone_elses_password = TicketSystemPasswordFactory(  # noqa: F841
        event=event, value="FATAL LEAK", assigned_at=now()
    )

    variables = {
        "input": {"eventId": get_global_id(event), "childId": get_global_id(child)}
    }

    executed = guardian_api_client.execute(
        ASSIGN_TICKET_SYSTEM_PASSWORD_MUTATION,
        variables=variables,
    )

    assert_match_error_code(executed, NO_FREE_TICKET_SYSTEM_PASSWORDS_ERROR)


def test_assign_ticket_system_password_not_own_child(guardian_api_client):
    event = EventFactory(ticket_system=Event.TICKETMASTER, published_at=now())
    another_child = ChildWithGuardianFactory()
    some_free_password = TicketSystemPasswordFactory(event=event)  # noqa: F841

    variables = {
        "input": {
            "eventId": get_global_id(event),
            "childId": get_global_id(another_child),
        }
    }

    # try to assign a password to someone else's child
    executed = guardian_api_client.execute(
        ASSIGN_TICKET_SYSTEM_PASSWORD_MUTATION,
        variables=variables,
    )

    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)
    assert not another_child.ticket_system_passwords.filter(event=event).exists()


# NOTE: api_client is for anonymous users
def test_verify_valid_ticket(api_client, snapshot):
    upcoming_occurrence = OccurrenceFactory(time=timezone.now())
    valid_enrolment = EnrolmentFactory(occurrence=upcoming_occurrence)
    executed = api_client.execute(
        VERIFY_TICKET_QUERY, variables={"referenceId": valid_enrolment.reference_id}
    )
    assert executed["data"]["verifyTicket"]["validity"] is True
    assert (
        executed["data"]["verifyTicket"]["occurrenceTime"]
        == upcoming_occurrence.time.isoformat()
    )
    assert (
        executed["data"]["verifyTicket"]["eventName"] == upcoming_occurrence.event.name
    )
    assert (
        executed["data"]["verifyTicket"]["venueName"] == upcoming_occurrence.venue.name
    )
    snapshot.assert_match(executed)


# NOTE: api_client is for anonymous users
def test_verify_invalid_ticket(api_client, snapshot):
    past_occurrence = OccurrenceFactory(time=timezone.now() - timedelta(days=1))
    invalid_enrolment = EnrolmentFactory(occurrence=past_occurrence)
    executed = api_client.execute(
        VERIFY_TICKET_QUERY, variables={"referenceId": invalid_enrolment.reference_id}
    )
    assert executed["data"]["verifyTicket"]["validity"] is False
    snapshot.assert_match(executed)


def test_erroneous_ticket_verification(api_client, snapshot):
    executed = api_client.execute(
        VERIFY_TICKET_QUERY, variables={"referenceId": "INVALID REFERENCE"}
    )
    assert executed["errors"][0]["message"] == "Could not decode the enrolment id"
    assert executed["data"]["verifyTicket"] is None
    snapshot.assert_match(executed)


def test_get_enrolment_reference_id_with_authorized_guardian(
    guardian_api_client,
    occurrence,
    child_with_user_guardian,
):
    EnrolmentFactory(occurrence=occurrence, child=child_with_user_guardian)

    executed = guardian_api_client.execute(
        GET_ENROLMENT_REFERENCE_ID_QUERY,
        variables={"id": to_global_id("ChildNode", child_with_user_guardian.id)},
    )
    assert (
        executed["data"]["child"]["enrolments"]["edges"][0]["node"]["referenceId"]
        is not None
    )


def test_get_enrolment_reference_id_with_unauthorized_guardian(
    guardian_api_client,
    occurrence,
    child_with_random_guardian,
):
    EnrolmentFactory(occurrence=occurrence, child=child_with_random_guardian)

    # Random user should not see the reference id
    executed = guardian_api_client.execute(
        GET_ENROLMENT_REFERENCE_ID_QUERY,
        variables={"id": to_global_id("ChildNode", child_with_random_guardian.id)},
    )
    assert executed["data"]["child"] is None


def test_get_enrolment_reference_id_from_public_api(
    api_client,
    occurrence,
    child_with_random_guardian,
):
    EnrolmentFactory(occurrence=occurrence, child=child_with_random_guardian)

    # Random user should not see the reference id
    executed = api_client.execute(
        GET_ENROLMENT_REFERENCE_ID_QUERY,
        variables={"id": to_global_id("ChildNode", child_with_random_guardian.id)},
    )
    assert executed["data"]["child"] is None
    assert_permission_denied(executed)
