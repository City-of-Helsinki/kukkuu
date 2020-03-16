from copy import deepcopy

import pytest
from graphql_relay import to_global_id

from common.tests.utils import assert_permission_denied
from venues.models import Venue


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


VENUES_QUERY = """
query Venues {
  venues {
    edges {
      node {
        name
        description
        address
        accessibilityInfo
        arrivalInstructions
        additionalInfo
        wcAndFacilities
        wwwUrl
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
              remainingCapacity
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
    name
    description
    address
    accessibilityInfo
    arrivalInstructions
    additionalInfo
    wcAndFacilities
    wwwUrl
    translations{
        name
        description
        address
        accessibilityInfo
        arrivalInstructions
        additionalInfo
        wcAndFacilities
        wwwUrl
        languageCode
    }
    occurrences{
      edges{
        node{
          time
          remainingCapacity
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
        wcAndFacilities
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
                "languageCode": "FI",
                "address": "Address",
                "accessibilityInfo": "Accessibility info",
                "arrivalInstructions": "Arrival instruction",
                "additionalInfo": "Additional info",
                "wcAndFacilities": "WC & Facilities",
                "wwwUrl": "www.url.com",
            }
        ],
    }
}

UPDATE_VENUE_MUTATION = """
mutation updateVenue($input: UpdateVenueMutationInput!) {
  updateVenue(input: $input) {
    venue {
      translations{
        languageCode
        name
        description
        address
        accessibilityInfo
        arrivalInstructions
        additionalInfo
        wcAndFacilities
        wwwUrl
      }
    }
  }
}
"""

UPDATE_VENUE_VARIABLES = {
    "input": {
        "id": "",
        "translations": [
            {
                "name": "Venue name",
                "description": "Venue description",
                "languageCode": "FI",
                "address": "Address",
                "accessibilityInfo": "Accessibility info",
                "arrivalInstructions": "Arrival instruction",
                "additionalInfo": "Additional info",
                "wcAndFacilities": "WC & Facilities",
                "wwwUrl": "www.url.com",
            }
        ],
    }
}

DELETE_VENUE_MUTATION = """
mutation DeleteVenue($input: DeleteVenueMutationInput!) {
  deleteVenue(input: $input) {
    __typename
  }
}
"""


def test_venues_query_unauthenticated(api_client):
    executed = api_client.execute(VENUES_QUERY)

    assert_permission_denied(executed)


def test_venues_query_normal_user(snapshot, user_api_client, venue):
    executed = user_api_client.execute(VENUES_QUERY)

    snapshot.assert_match(executed)


def test_venue_query_unauthenticated(api_client, venue):
    variables = {"id": to_global_id("VenueNode", venue.id)}
    executed = api_client.execute(VENUE_QUERY, variables=variables)

    assert_permission_denied(executed)


def test_venue_query_normal_user(snapshot, user_api_client, venue):
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


def test_update_venue_permission_denied(api_client, user_api_client):
    executed = api_client.execute(
        UPDATE_VENUE_MUTATION, variables=UPDATE_VENUE_VARIABLES
    )
    assert_permission_denied(executed)

    executed = user_api_client.execute(
        UPDATE_VENUE_MUTATION, variables=UPDATE_VENUE_VARIABLES
    )
    assert_permission_denied(executed)


def test_update_venue_staff_user(snapshot, staff_api_client, venue):
    venue_variables = deepcopy(UPDATE_VENUE_VARIABLES)
    venue_variables["input"]["id"] = to_global_id("VenueNode", venue.id)
    executed = staff_api_client.execute(
        UPDATE_VENUE_MUTATION, variables=venue_variables
    )
    snapshot.assert_match(executed)


def test_delete_venue_permission_denied(api_client, user_api_client):
    executed = api_client.execute(
        DELETE_VENUE_MUTATION, variables={"input": {"id": ""}}
    )
    assert_permission_denied(executed)

    executed = user_api_client.execute(
        DELETE_VENUE_MUTATION, variables={"input": {"id": ""}}
    )
    assert_permission_denied(executed)


def test_delete_venue_staff_user(staff_api_client, venue):
    staff_api_client.execute(
        DELETE_VENUE_MUTATION,
        variables={"input": {"id": to_global_id("VenueNode", venue.id)}},
    )
    assert Venue.objects.count() == 0
