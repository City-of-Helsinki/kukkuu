from copy import deepcopy
from datetime import datetime, timedelta
from typing import Dict

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import activate
from graphql_relay import to_global_id
from parler.utils.context import switch_language
from projects.factories import ProjectFactory
from projects.models import Project

from children.factories import ChildWithGuardianFactory
from common.tests.utils import assert_match_error_code, assert_permission_denied
from common.utils import get_global_id
from events.factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    OccurrenceFactory,
)
from events.models import Enrolment, Event, EventGroup, Occurrence
from kukkuu.consts import (
    CHILD_ALREADY_JOINED_EVENT_ERROR,
    DATA_VALIDATION_ERROR,
    EVENT_ALREADY_PUBLISHED_ERROR,
    EVENT_GROUP_ALREADY_PUBLISHED_ERROR,
    EVENT_GROUP_NOT_READY_FOR_PUBLISHING_ERROR,
    GENERAL_ERROR,
    INELIGIBLE_OCCURRENCE_ENROLMENT,
    MISSING_DEFAULT_TRANSLATION_ERROR,
    OBJECT_DOES_NOT_EXIST_ERROR,
    OCCURRENCE_IS_FULL_ERROR,
    PAST_ENROLMENT_ERROR,
    PAST_OCCURRENCE_ERROR,
    SINGLE_EVENTS_DISALLOWED_ERROR,
)
from kukkuu.exceptions import QueryTooDeepError
from kukkuu.schema import schema
from kukkuu.views import DepthAnalysisBackend
from venues.factories import VenueFactory


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


EVENTS_QUERY = """
query Events {
  events {
    edges {
      node {
        translations{
          name
          description
          shortDescription
          imageAltText
          languageCode
        }
        project{
          year
        }
        name
        description
        shortDescription
        duration
        image
        imageAltText
        participantsPerInvite
        capacityPerOccurrence
        publishedAt
        createdAt
        updatedAt
        ticketSystem {
          type
        }
        occurrences {
          edges {
            node {
              remainingCapacity
              enrolmentCount
              time
              venue {
                translations{
                  name
                  description
                  languageCode
                }
              }
            }
          }
        }
      }
    }
  }
}

"""

EVENT_QUERY = """
query Event($id:ID!) {
  event(id: $id) {
    translations{
      name
      shortDescription
      description
      imageAltText
      languageCode
    }
    project{
      year
    }
    name
    description
    shortDescription
    image
    imageAltText
    participantsPerInvite
    capacityPerOccurrence
    publishedAt
    createdAt
    updatedAt
    duration
    ticketSystem {
      type
    }
    occurrences{
      edges{
        node{
          time
          remainingCapacity
          enrolmentCount
          venue{
            translations{
              name
              description
              languageCode
            }
          }
        }
      }
    }
  }
}
"""

EVENTS_FILTER_QUERY = """
query Events($projectId: ID) {
  events(projectId: $projectId) {
    edges {
      node {
        name
      }
    }
  }
}
"""

OCCURRENCES_QUERY = """
query Occurrences {
  occurrences {
    edges {
      node {
        time
        remainingCapacity
        enrolmentCount
        event {
          translations {
            name
            shortDescription
            description
            languageCode
          }
          image
          participantsPerInvite
          capacityPerOccurrence
          publishedAt
          duration
        }
        venue{
          translations{
            name
            description
            address
            accessibilityInfo
            arrivalInstructions
            additionalInfo
            wwwUrl
            languageCode
          }
        }
      }
    }
  }
}
"""

OCCURRENCES_FILTER_QUERY = """
query Occurrences($date: Date, $time: Time, $upcoming: Boolean, $venueId: String,
                  $eventId: String, $occurrenceLanguage: String, $projectId: String,
                  $upcomingWithLeeway: Boolean) {
  occurrences(date: $date, time: $time, upcoming: $upcoming, venueId: $venueId,
              eventId: $eventId, occurrenceLanguage: $occurrenceLanguage,
              projectId: $projectId, upcomingWithLeeway: $upcomingWithLeeway) {
    edges {
      node {
        time
      }
    }
  }
}
"""

OCCURRENCE_QUERY = """
query Occurrence($id: ID!) {
  occurrence(id: $id){
    enrolments{
        edges{
          node{
            child{
              firstName
            }
          }
        }
    }
    time
    remainingCapacity
    enrolmentCount
    occurrenceLanguage
    event {
      translations {
        name
        shortDescription
        description
        languageCode
      }
      image
      participantsPerInvite
      capacityPerOccurrence
      publishedAt
      duration
    }
    venue{
      translations{
        name
        description
        address
        accessibilityInfo
        arrivalInstructions
        additionalInfo
        wwwUrl
        languageCode
      }
    }
  }
}
"""

ADD_EVENT_MUTATION = """
mutation AddEvent($input: AddEventMutationInput!) {
  addEvent(input: $input) {
    event {
      translations{
        languageCode
        name
        description
        imageAltText
        shortDescription
      }
      project{
        year
      }
      duration
      image
      imageAltText
      participantsPerInvite
      capacityPerOccurrence
      publishedAt
      readyForEventGroupPublishing
      ticketSystem {
        type
      }
    }
  }
}
"""

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

UPDATE_EVENT_MUTATION = """
mutation UpdateEvent($input: UpdateEventMutationInput!) {
  updateEvent(input: $input) {
    event {
      translations{
        name
        shortDescription
        description
        imageAltText
        languageCode
      }
      image
      imageAltText
      participantsPerInvite
      capacityPerOccurrence
      duration
      ticketSystem {
        type
      }
      occurrences{
        edges{
          node{
            time
          }
        }
      }
      readyForEventGroupPublishing
    }
  }
}
"""

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

PUBLISH_EVENT_MUTATION = """
mutation PublishEvent($input: PublishEventMutationInput!) {
  publishEvent(input: $input) {
    event {
      publishedAt
    }
  }
}
"""

PUBLISH_EVENT_VARIABLES = {"input": {"id": ""}}

DELETE_EVENT_MUTATION = """
mutation DeleteEvent($input: DeleteEventMutationInput!) {
  deleteEvent(input: $input) {
    __typename
  }
}
"""

ADD_OCCURRENCE_MUTATION = """
mutation AddOccurrence($input: AddOccurrenceMutationInput!) {
  addOccurrence(input: $input) {
    occurrence{
      event{
        createdAt
      }
      venue {
        createdAt
      }
      time
      occurrenceLanguage
      capacity
      capacityOverride
    }
  }
}

"""

ADD_OCCURRENCE_VARIABLES = {
    "input": {"eventId": "", "venueId": "", "time": "1986-12-12T16:40:48+00:00"}
}

UPDATE_OCCURRENCE_MUTATION = """
mutation UpdateOccurrence($input: UpdateOccurrenceMutationInput!) {
  updateOccurrence(input: $input) {
    occurrence{
      event{
        createdAt
      }
      venue {
        createdAt
      }
      time
      occurrenceLanguage
      enrolmentCount
      remainingCapacity
      capacity
      capacityOverride
    }
  }
}

"""

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

DELETE_OCCURRENCE_MUTATION = """
mutation DeleteOccurrence($input: DeleteOccurrenceMutationInput!) {
  deleteOccurrence(input: $input) {
    __typename
  }
}

"""

ENROL_OCCURRENCE_MUTATION = """
mutation EnrolOccurrence($input: EnrolOccurrenceMutationInput!) {
  enrolOccurrence(input: $input) {
    enrolment{
      child{
        firstName
      }
      occurrence {
        time
      }
      createdAt
    }
  }
}

"""

ENROL_OCCURRENCE_VARIABLES = {"input": {"occurrenceId": "", "childId": ""}}

UNENROL_OCCURRENCE_MUTATION = """
mutation UnenrolOccurrence($input: UnenrolOccurrenceMutationInput!) {
  unenrolOccurrence(input: $input) {
    occurrence{
        time
    }
    child{
        firstName
    }
  }
}

"""

UNENROL_OCCURRENCE_VARIABLES = {"input": {"occurrenceId": "", "childId": ""}}

SET_ENROLMENT_ATTENDANCE_MUTATION = """
mutation SetEnrolmentAttendance($input: SetEnrolmentAttendanceMutationInput!) {
  setEnrolmentAttendance(input: $input) {
    enrolment {
      attended
    }
  }
}

"""


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
    event_variables["input"]["id"] = to_global_id("EventNode", event.id)
    event_variables["input"]["eventGroupId"] = to_global_id(
        "EventGroupNode", event_group.id
    )
    executed = project_user_api_client.execute(
        UPDATE_EVENT_MUTATION, variables=event_variables
    )
    snapshot.assert_match(executed)


def test_update_event_ready_for_event_group_publishing(
    snapshot, project_user_api_client, event, event_group
):
    variables = {
        "input": {"id": get_global_id(event), "readyForEventGroupPublishing": True},
    }
    executed = project_user_api_client.execute(
        UPDATE_EVENT_MUTATION, variables=variables
    )
    snapshot.assert_match(executed)


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


def test_enrol_occurrence(
    api_client, guardian_api_client, snapshot, occurrence, child_with_user_guardian
):
    non_authen_executed = api_client.execute(
        ENROL_OCCURRENCE_MUTATION, variables=ENROL_OCCURRENCE_VARIABLES
    )
    assert_permission_denied(non_authen_executed)

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
    guardian_api_client, snapshot, occurrence, child_with_user_guardian
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


def test_enrol_occurrence_not_allowed(
    guardian_api_client, snapshot, occurrence, child_with_random_guardian
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
        child__first_name="ME ME ME",
        child__project=project,
        occurrence__event__project=project,
    )
    EnrolmentFactory(
        child__first_name="NOT me",
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
                    firstName
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
        event__project=next_project, venue__project=next_project
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


def test_api_query_depth(snapshot, guardian_api_client, event):
    # Depth 6
    query = """
    query Events {
      events {
        edges {
          node {
            project{
              events{
                name
              }
            }
          }
        }
      }
    }
    """
    backend = DepthAnalysisBackend(max_depth=5)
    with pytest.raises(QueryTooDeepError):
        backend.document_from_string(schema=schema, document_string=query)

    backend = DepthAnalysisBackend(max_depth=6)
    document = backend.document_from_string(schema=schema, document_string=query)
    assert document is not None


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
    project_user_api_client, occurrence, another_project,
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


EVENT_GROUP_QUERY = """
query EventGroup($id: ID!) {
  eventGroup(id: $id) {
    translations{
      name
      shortDescription
      description
      imageAltText
      languageCode
    }
    project {
      year
    }
    name
    description
    shortDescription
    image
    imageAltText
    publishedAt
    createdAt
    updatedAt
    events {
      edges {
        node {
          __typename
          name
        }
      }
    }
  }
}
"""


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


EVENTS_AND_EVENT_GROUPS_SIMPLE_QUERY = """
query EventsAndEventGroups($projectId: ID) {
  eventsAndEventGroups(projectId: $projectId) {
    edges {
      node {
        ... on EventNode {
          __typename
          name
        }
        ... on EventGroupNode {
          __typename
          name
        }
      }
    }
  }
}
"""


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


ADD_EVENT_GROUP_MUTATION = """
mutation AddEventGroup($input: AddEventGroupMutationInput!) {
  addEventGroup(input: $input) {
    eventGroup {
      translations{
        languageCode
        name
        description
        imageAltText
        shortDescription
      }
      project{
        year
      }
      image
      imageAltText
      publishedAt
    }
  }
}
"""

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


UPDATE_EVENT_GROUP_MUTATION = """
mutation UpdateEventGroup($input: UpdateEventGroupMutationInput!) {
  updateEventGroup(input: $input) {
    eventGroup {
      translations{
        name
        shortDescription
        description
        imageAltText
        languageCode
      }
      image
    }
  }
}
"""

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


DELETE_EVENT_GROUP_MUTATION = """
mutation DeleteEventGroup($input: DeleteEventGroupMutationInput!) {
  deleteEventGroup(input: $input) {
    __typename
  }
}
"""


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


PUBLISH_EVENT_GROUP_MUTATION = """
mutation PublishEventGroup($input: PublishEventGroupMutationInput!) {
  publishEventGroup(input: $input) {
    eventGroup {
      publishedAt
      events {
        edges {
          node {
            publishedAt
          }
        }
      }
    }
  }
}
"""

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


EVENT_GROUP_EVENTS_FILTER_QUERY = """
query EventGroup($id: ID!, $availableForChild: String) {
  eventGroup(id: $id) {
    events(availableForChild: $availableForChild) {
      edges {
        node {
          name
        }
      }
    }
  }
}
"""


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
