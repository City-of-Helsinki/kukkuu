from copy import deepcopy

import pytest
from django.conf import settings
from django.utils import translation
from graphql_relay import to_global_id

from common.tests.utils import assert_permission_denied
from common.utils import get_global_id
from venues.factories import SystemVenueFactory, VenueFactory
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
    project{
      year
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
      project{
        year
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
        "projectId": "",
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
      project{
        year
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

VENUES_FILTER_QUERY = """
query Venues($projectId: ID!) {
  venues(projectId: $projectId) {
    edges {
      node {
        name
      }
    }
  }
}
"""


def test_venues_project_filter(
    snapshot, two_project_user_api_client, project, another_project
):
    VenueFactory(name="Should be returned", project=project)
    VenueFactory(name="Should NOT be returned", project=another_project)

    variables = {"projectId": get_global_id(project)}

    executed = two_project_user_api_client.execute(
        VENUES_FILTER_QUERY, variables=variables
    )

    snapshot.assert_match(executed)


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


def test_add_venue_permission_denied(unauthorized_user_api_client, project):
    venue_variables = deepcopy(ADD_VENUE_VARIABLES)
    venue_variables["input"]["projectId"] = to_global_id("ProjectNode", project.id)

    executed = unauthorized_user_api_client.execute(
        ADD_VENUE_MUTATION, variables=venue_variables
    )
    assert_permission_denied(executed)


def test_add_venue_project_user(snapshot, project_user_api_client, project):
    venue_variables = deepcopy(ADD_VENUE_VARIABLES)
    venue_variables["input"]["projectId"] = to_global_id("ProjectNode", project.id)
    executed = project_user_api_client.execute(
        ADD_VENUE_MUTATION, variables=venue_variables
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


def test_update_venue_project_user(snapshot, project_user_api_client, venue):
    venue_variables = deepcopy(UPDATE_VENUE_VARIABLES)
    venue_variables["input"]["id"] = to_global_id("VenueNode", venue.id)
    executed = project_user_api_client.execute(
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


def test_delete_venue_project_user(project_user_api_client, venue):
    project_user_api_client.execute(
        DELETE_VENUE_MUTATION,
        variables={"input": {"id": to_global_id("VenueNode", venue.id)}},
    )
    assert Venue.objects.filter(is_system=False).count() == 0


@pytest.mark.parametrize("request_language", ("fi", "en"))
def test_venues_query_ordering(snapshot, project_user_api_client, request_language):
    venue = VenueFactory(name="3 in Finnish")
    VenueFactory(name="4 in Finnish")
    VenueFactory(name="2 in Finnish")

    # this should not affect the ordering
    venue.set_current_language("en")
    venue.name = "1 in English"
    venue.save()

    with translation.override(request_language):
        executed = project_user_api_client.execute(
            """
    query Venues {
      venues {
        edges {
          node {
            name
          }
        }
      }
    }
    """
        )

    snapshot.assert_match(executed)


def test_venues_query_excludes_system_venue(project_user_api_client, project):
    SystemVenueFactory()
    VenueFactory(name="Regular Venue", project=project)

    executed = project_user_api_client.execute(
        """
        query Venues {
          venues {
            edges {
              node {
                name
                isSystem
              }
            }
          }
        }
        """
    )
    assert executed.get("errors") is None
    edges = executed["data"]["venues"]["edges"]
    venue_names = [edge["node"]["name"] for edge in edges]
    assert "Regular Venue" in venue_names
    assert settings.KUKKUU_DEFAULT_VENUE_NAME not in venue_names
    assert all(not edge["node"]["isSystem"] for edge in edges)


def test_system_venue_query_by_id(project_user_api_client):
    system_venue = SystemVenueFactory()

    executed = project_user_api_client.execute(
        """
        query Venue($id: ID!) {
          venue(id: $id) {
            name
            isSystem
            project {
              year
            }
          }
        }
        """,
        variables={"id": get_global_id(system_venue)},
    )
    assert executed.get("errors") is None
    data = executed["data"]["venue"]
    assert data["name"] == settings.KUKKUU_DEFAULT_VENUE_NAME
    assert data["isSystem"] is True
    assert data["project"] is None


def test_delete_system_venue_mutation_rejected(project_user_api_client):
    system_venue = SystemVenueFactory()

    executed = project_user_api_client.execute(
        DELETE_VENUE_MUTATION,
        variables={"input": {"id": get_global_id(system_venue)}},
    )
    # Project user lacks permission to administer system venue
    assert_permission_denied(executed)


def test_delete_system_venue_mutation_rejected_for_superuser(project_user_api_client):
    project_user_api_client.user.is_superuser = True
    project_user_api_client.user.save()

    system_venue = SystemVenueFactory()

    executed = project_user_api_client.execute(
        DELETE_VENUE_MUTATION,
        variables={"input": {"id": get_global_id(system_venue)}},
    )
    assert executed.get("errors") is not None
    assert "The system venue cannot be deleted" in str(executed["errors"])


def test_venues_query_filter_by_name(project_user_api_client, project):
    VenueFactory(name="Kirjasto Oodi", project=project)
    VenueFactory(name="Kaapelitehdas", project=project)

    query = """
    query Venues($name: String) {
      venues(name: $name) {
        edges {
          node {
            name
          }
        }
      }
    }
    """
    # Matching search (case-insensitive substring)
    res_match = project_user_api_client.execute(query, variables={"name": "oodi"})
    assert res_match.get("errors") is None
    names = [e["node"]["name"] for e in res_match["data"]["venues"]["edges"]]
    assert names == ["Kirjasto Oodi"]

    # Partial match on multiple
    res_part = project_user_api_client.execute(query, variables={"name": "a"})
    assert res_part.get("errors") is None
    part_names = [e["node"]["name"] for e in res_part["data"]["venues"]["edges"]]
    assert "Kirjasto Oodi" in part_names
    assert "Kaapelitehdas" in part_names

    # Non-matching search
    res_none = project_user_api_client.execute(query, variables={"name": "nonexistent"})
    assert res_none.get("errors") is None
    assert len(res_none["data"]["venues"]["edges"]) == 0
