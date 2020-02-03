from copy import deepcopy
from typing import Dict

import pytest
from graphql_relay import to_global_id

from common.tests.utils import assert_permission_denied
from events.factories import EventFactory
from events.models import Event, Occurrence


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
          languageCode
        }
        duration
        image
        participantsPerInvite
        capacityPerOccurrence
        publishedAt
        createdAt
        updatedAt
        occurrences {
          edges {
            node {
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
      languageCode
    }
    image
    participantsPerInvite
    capacityPerOccurrence
    publishedAt
    createdAt
    updatedAt
    duration
    occurrences{
      edges{
        node{
          time
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

OCCURRENCES_QUERY = """
query Occurrences {
  occurrences {
    edges {
      node {
        time
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

OCCURRENCE_QUERY = """
query Occurrence($id: ID!) {
  occurrence(id: $id){
    time
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
        shortDescription
      }
      duration
      image
      participantsPerInvite
      capacityPerOccurrence
      publishedAt
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
                "languageCode": "fi",
            }
        ],
        "duration": 1000,
        # "image": None,
        "participantsPerInvite": "family",
        "capacityPerOccurrence": 30,
        "publishedAt": "1986-12-12T16:40:48+00:00",
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
        languageCode
      }
      participantsPerInvite
      capacityPerOccurrence
      duration
      occurrences{
        edges{
          node{
            id
          }
        }
      }
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
                "languageCode": "sv",
            }
        ],
        "duration": 1000,
        "participantsPerInvite": "family",
        "capacityPerOccurrence": 30,
    }
}

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
        id,
      }
      venue {
        id
      }
        time
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
      id
      event{
        id
      }
      venue {
        id
      }
        time
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
    }
}

DELETE_OCCURRENCE_MUTATION = """
mutation DeleteOccurrence($input: DeleteOccurrenceMutationInput!) {
  deleteOccurrence(input: $input) {
    __typename
  }
}

"""


def test_events_query_unauthenticated(api_client, event, snapshot):
    executed = api_client.execute(EVENTS_QUERY)

    snapshot.assert_match(executed)


def test_events_query_normal_user(snapshot, user_api_client, event):
    executed = user_api_client.execute(EVENTS_QUERY)

    snapshot.assert_match(executed)


def test_event_query_unauthenticated(api_client, event, snapshot):
    variables = {"id": to_global_id("EventNode", event.id)}
    executed = api_client.execute(EVENT_QUERY, variables=variables)

    snapshot.assert_match(executed)


def test_event_query_normal_user(snapshot, user_api_client, event):
    variables = {"id": to_global_id("EventNode", event.id)}
    executed = user_api_client.execute(EVENT_QUERY, variables=variables)

    snapshot.assert_match(executed)


def test_occurrences_query_unauthenticated(api_client, occurrence, snapshot):
    executed = api_client.execute(OCCURRENCES_QUERY)

    snapshot.assert_match(executed)


def test_occurrences_query_normal_user(snapshot, user_api_client, occurrence):
    executed = user_api_client.execute(OCCURRENCES_QUERY)

    snapshot.assert_match(executed)


def test_occurrence_query_unauthenticated(api_client, occurrence, snapshot):
    variables = {"id": to_global_id("OccurrenceNode", occurrence.id)}
    executed = api_client.execute(OCCURRENCE_QUERY, variables=variables)

    snapshot.assert_match(executed)


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


def test_add_event_staff_user(snapshot, staff_api_client):
    executed = staff_api_client.execute(
        ADD_EVENT_MUTATION, variables=ADD_EVENT_VARIABLES
    )
    snapshot.assert_match(executed)


def test_add_occurrence_permission_denied(api_client, user_api_client):
    executed = api_client.execute(
        ADD_OCCURRENCE_MUTATION, variables=ADD_OCCURRENCE_VARIABLES
    )
    assert_permission_denied(executed)

    executed = user_api_client.execute(
        ADD_OCCURRENCE_MUTATION, variables=ADD_OCCURRENCE_VARIABLES
    )
    assert_permission_denied(executed)


def test_add_occurrence_staff_user(snapshot, staff_api_client, event, venue):
    occurrence_variables = deepcopy(ADD_OCCURRENCE_VARIABLES)
    occurrence_variables["input"]["eventId"] = to_global_id("EventNode", event.id)
    occurrence_variables["input"]["venueId"] = to_global_id("VenueNode", venue.id)
    executed = staff_api_client.execute(
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


def test_update_occurrence_staff_user(snapshot, staff_api_client, occurrence):
    occurrence_variables = deepcopy(UPDATE_OCCURRENCE_VARIABLES)
    occurrence_variables["input"]["id"] = to_global_id("OccurrenceNode", occurrence.id)
    occurrence_variables["input"]["eventId"] = to_global_id(
        "EventNode", occurrence.event.id
    )
    occurrence_variables["input"]["venueId"] = to_global_id(
        "VenueNode", occurrence.venue.id
    )
    executed = staff_api_client.execute(
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


def test_delete_occurrence_staff_user(staff_api_client, occurrence):
    staff_api_client.execute(
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


def test_update_event_staff_user(snapshot, staff_api_client, event):
    event_variables = deepcopy(UPDATE_EVENT_VARIABLES)
    event_variables["input"]["id"] = to_global_id("EventNode", event.id)
    executed = staff_api_client.execute(
        UPDATE_EVENT_MUTATION, variables=event_variables
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


def test_delete_event_staff_user(staff_api_client, event):
    staff_api_client.execute(
        DELETE_EVENT_MUTATION,
        variables={"input": {"id": to_global_id("EventNode", event.id)}},
    )
    assert Event.objects.count() == 0


def test_update_event_translations(staff_api_client, event):
    event = EventFactory()
    assert event.translations.count() == 1
    event_variables = deepcopy(UPDATE_EVENT_VARIABLES)
    event_variables["input"]["id"] = to_global_id("EventNode", event.id)

    # Test add translation
    new_translation: Dict[str, (list, str)] = {
        "name": "Event name",
        "description": "Event description",
        "shortDescription": "Event short description",
        "languageCode": "sv",
    }
    event_variables["input"]["translations"].append(new_translation)
    staff_api_client.execute(UPDATE_EVENT_MUTATION, variables=event_variables)
    assert event.has_translation(new_translation["languageCode"])

    # Test delete translation
    event_variables["input"]["deleteTranslations"] = [new_translation["languageCode"]]
    staff_api_client.execute(UPDATE_EVENT_MUTATION, variables=event_variables)
    assert not event.has_translation(new_translation["languageCode"])

    # Test invalid translation
    new_translation["languageCode"] = "foo"
    staff_api_client.execute(UPDATE_EVENT_MUTATION, variables=event_variables)
    assert not event.has_translation(new_translation["languageCode"])
