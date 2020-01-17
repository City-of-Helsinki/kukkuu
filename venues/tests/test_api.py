import pytest
from graphql_relay import to_global_id

from common.tests.utils import assert_permission_denied
from events.factories import OccurrenceFactory


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


VENUES_QUERY = """
query Venues {
  venues {
    edges {
      node {
        translations {
          name
          description
          address
          accessibilityInfo
          arrivalInstructions
          additionalInfo
          wwwUrl
          languageCode
        }
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
            }
          }
        }
      }
    }
  }
}
"""

VENUE_QUERY = """
query Venue($id: ID!) {
  venue(id: $id){
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
    occurrences{
      edges{
        node{
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
        }
      }
    }
  }
}
"""

ADD_VENUE_MUTATION = """
mutation AddVenue($input: AddVenueMutationInput!) {
  addVenue(input: $input) {
    venue {
      translations{
        languageCode
        name
        description
        address
        accessibilityInfo
        arrivalInstructions
        additionalInfo
        wwwUrl
      }
    }
  }
}
"""

ADD_VENUE_VARIABLES = {
    "input": {
        "translations": [
            {
                "name": "Venue name",
                "description": "Venue description",
                "languageCode": "fi",
                "address": "Address",
                "accessibilityInfo": "Accessibility info",
                "arrivalInstructions": "Arrival instruction",
                "additionalInfo": "Additional info",
                "wwwUrl": "www.url.com",
            }
        ],
    }
}


def test_venues_query_unauthenticated(api_client):
    executed = api_client.execute(VENUES_QUERY)

    assert_permission_denied(executed)


def test_venues_query_normal_user(snapshot, user_api_client):
    OccurrenceFactory()

    executed = user_api_client.execute(VENUES_QUERY)

    snapshot.assert_match(executed)


def test_venue_query_unauthenticated(api_client):
    occurrence = OccurrenceFactory()
    venue = occurrence.venue
    variables = {"id": to_global_id("VenueNode", venue.id)}
    executed = api_client.execute(VENUE_QUERY, variables=variables)

    assert_permission_denied(executed)


def test_venue_query_normal_user(snapshot, user_api_client):
    occurrence = OccurrenceFactory()
    venue = occurrence.venue
    variables = {"id": to_global_id("VenueNode", venue.id)}
    executed = user_api_client.execute(VENUE_QUERY, variables=variables)

    snapshot.assert_match(executed)


def test_add_venue_permission_denied(api_client, user_api_client):
    executed = api_client.execute(ADD_VENUE_MUTATION, variables=ADD_VENUE_VARIABLES)
    assert_permission_denied(executed)

    executed = user_api_client.execute(
        ADD_VENUE_MUTATION, variables=ADD_VENUE_VARIABLES
    )
    assert_permission_denied(executed)


def test_add_venue_staff_user(snapshot, staff_api_client):
    executed = staff_api_client.execute(
        ADD_VENUE_MUTATION, variables=ADD_VENUE_VARIABLES
    )
    snapshot.assert_match(executed)
