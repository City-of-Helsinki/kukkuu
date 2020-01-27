from copy import deepcopy

import pytest
from graphql_relay import to_global_id

from common.tests.utils import assert_permission_denied
from events.factories import EventFactory, OccurrenceFactory
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


def test_events_query_unauthenticated(api_client):
    executed = api_client.execute(EVENTS_QUERY)

    assert_permission_denied(executed)


def test_events_query_normal_user(snapshot, user_api_client):
    OccurrenceFactory()

    executed = user_api_client.execute(EVENTS_QUERY)

    snapshot.assert_match(executed)


def test_event_query_unauthenticated(api_client):
    event = EventFactory()
    variables = {"id": to_global_id("EventNode", event.id)}
    executed = api_client.execute(EVENT_QUERY, variables=variables)

    assert_permission_denied(executed)


def test_event_query_normal_user(snapshot, user_api_client):
    event = EventFactory()
    variables = {"id": to_global_id("EventNode", event.id)}
    executed = user_api_client.execute(EVENT_QUERY, variables=variables)

    snapshot.assert_match(executed)


def test_occurrences_query_unauthenticated(api_client):
    executed = api_client.execute(OCCURRENCES_QUERY)

    assert_permission_denied(executed)


def test_occurrences_query_normal_user(snapshot, user_api_client):
    OccurrenceFactory()

    executed = user_api_client.execute(OCCURRENCES_QUERY)

    snapshot.assert_match(executed)


def test_occurrence_query_unauthenticated(api_client):
    occurrence = OccurrenceFactory()
    variables = {"id": to_global_id("OccurrenceNode", occurrence.id)}
    executed = api_client.execute(OCCURRENCE_QUERY, variables=variables)

    assert_permission_denied(executed)


def test_occurrence_query_normal_user(snapshot, user_api_client):
    occurrence = OccurrenceFactory()
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


def test_add_occurrence_staff_user(snapshot, staff_api_client):
    event = EventFactory()
    venue = VenueFactory()
    occurrence_variables = deepcopy(ADD_OCCURRENCE_VARIABLES)
    occurrence_variables["input"]["eventId"] = to_global_id("EventNode", event.id)
    occurrence_variables["input"]["venueId"] = to_global_id("VenueNode", venue.id)
    executed = staff_api_client.execute(
        ADD_OCCURRENCE_MUTATION, variables=occurrence_variables
    )
    snapshot.assert_match(executed)
