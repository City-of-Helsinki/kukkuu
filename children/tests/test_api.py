from copy import deepcopy
from datetime import date, datetime, timedelta

import pytest
import pytz
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import localtime, now
from freezegun import freeze_time
from graphene.utils.str_converters import to_snake_case
from graphql_relay import to_global_id
from guardian.shortcuts import assign_perm

from children.factories import ChildWithGuardianFactory
from common.tests.utils import assert_match_error_code, assert_permission_denied
from common.utils import get_global_id, get_node_id_from_global_id
from events.factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    OccurrenceFactory,
)
from kukkuu.consts import (
    API_USAGE_ERROR,
    DATA_VALIDATION_ERROR,
    GENERAL_ERROR,
    INVALID_EMAIL_FORMAT_ERROR,
    MAX_NUMBER_OF_CHILDREN_PER_GUARDIAN_ERROR,
    OBJECT_DOES_NOT_EXIST_ERROR,
)
from languages.models import Language
from projects.factories import ProjectFactory
from users.factories import GuardianFactory
from users.models import Guardian

from ..models import Child, Relationship


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture(params=("1234x", ""))
def invalid_postal_code(request):
    return request.param


@pytest.fixture(params=[0, 1])
def illegal_birthdate(request):
    # these dates cannot be set to params directly because now() would not be
    # the faked one
    return (
        date(2019, 10, 10),  # wrong year
        localtime(now()).date() + timedelta(days=1),  # in the future
    )[request.param]


def assert_child_matches_data(child_obj, child_data):
    child_data = child_data or {}
    for field_name in ("firstName", "lastName", "birthDate", "postalCode"):
        if field_name in child_data:
            assert (
                str(getattr(child_obj, to_snake_case(field_name)))
                == child_data[field_name]
            )


def assert_relationship_matches_data(relationship_obj, relationship_data):
    relationship_data = relationship_data or {}
    if "type" in relationship_data:
        assert relationship_obj.type == relationship_data.get("type", "").lower()


def assert_guardian_matches_data(guardian_obj, guardian_data):
    guardian_data = guardian_data or {}
    for field_name in ("firstName", "lastName", "phoneNumber", "email"):
        if field_name in guardian_data:
            assert (
                str(getattr(guardian_obj, to_snake_case(field_name)))
                == guardian_data[field_name]
            )
    if "language" in guardian_data:
        assert guardian_obj.language == guardian_data["language"].lower()

    if "languagesSpokenAtHome" in guardian_data:
        language_ids = [
            get_node_id_from_global_id(l, "LanguageNode")
            for l in guardian_data["languagesSpokenAtHome"]
        ]
        assert set(guardian_obj.languages_spoken_at_home.all()) == set(
            Language.objects.filter(id__in=language_ids)
        )


SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION = """
mutation SubmitChildrenAndGuardian($input: SubmitChildrenAndGuardianMutationInput!) {
  submitChildrenAndGuardian(input: $input) {
    children {
      firstName
      lastName
      birthdate
      postalCode
      relationships {
        edges {
          node {
            type
            guardian {
              firstName
              lastName
              phoneNumber
              email
            }
          }
        }
      }
    }
    guardian {
      firstName
      lastName
      phoneNumber
      email
      languagesSpokenAtHome {
        edges {
          node {
            alpha3Code
          }
        }
      }
    }
  }
}
"""

CHILDREN_DATA = [
    {
        "firstName": "Matti",
        "lastName": "Mainio",
        "birthdate": "2020-01-01",
        "postalCode": "00840",
        "relationship": {"type": "OTHER_GUARDIAN"},
    },
    {
        "firstName": "Jussi",
        "lastName": "Juonio",
        "birthdate": "2020-02-02",
        "postalCode": "00820",
    },
]

GUARDIAN_DATA = {
    "firstName": "Gulle",
    "lastName": "Guardian",
    "phoneNumber": "777-777777",
    "language": "FI",
}

SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES = {
    "input": {"children": CHILDREN_DATA, "guardian": GUARDIAN_DATA}
}


def test_submit_children_and_guardian_unauthenticated(api_client):
    executed = api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION,
        variables=SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES,
    )

    assert_permission_denied(executed)


def test_submit_children_and_guardian(snapshot, user_api_client, languages):
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    variables["input"]["guardian"]["languagesSpokenAtHome"] = [
        get_global_id(language) for language in languages[0:2]
    ]  # fin, swe

    executed = user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION, variables=variables
    )

    snapshot.assert_match(executed)

    guardian = Guardian.objects.last()
    assert_guardian_matches_data(guardian, variables["input"]["guardian"])

    for child, child_data in zip(
        Child.objects.order_by("birthdate"), variables["input"]["children"]
    ):
        assert_child_matches_data(child, child_data)
        relationship = Relationship.objects.get(guardian=guardian, child=child)
        assert_relationship_matches_data(relationship, child_data.get("relationship"))


def test_submit_children_and_guardian_with_email(snapshot, user_api_client):
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    variables["input"]["guardian"]["email"] = "updated_email@example.com"

    executed = user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION, variables=variables
    )

    snapshot.assert_match(executed)

    guardian = Guardian.objects.last()
    assert_guardian_matches_data(guardian, variables["input"]["guardian"])


def test_submit_children_and_guardian_one_child_required(snapshot, user_api_client):
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    variables["input"]["children"] = []

    executed = user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION, variables=variables
    )

    assert_match_error_code(executed, API_USAGE_ERROR)
    assert "At least one child is required." in str(executed["errors"])


def test_submit_children_and_guardian_postal_code_validation(
    user_api_client, invalid_postal_code
):
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    variables["input"]["children"][0]["postalCode"] = invalid_postal_code

    executed = user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION, variables=variables
    )

    assert_match_error_code(executed, DATA_VALIDATION_ERROR)
    assert "Postal code must be 5 digits" in str(executed["errors"])


def test_submit_children_and_guardian_birthdate_validation(
    user_api_client, illegal_birthdate
):
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    variables["input"]["children"][0]["birthdate"] = illegal_birthdate

    executed = user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION, variables=variables
    )

    assert_match_error_code(executed, DATA_VALIDATION_ERROR)
    assert "Illegal birthdate." in str(executed["errors"])


def test_submit_children_and_guardian_can_be_done_only_once(guardian_api_client):
    executed = guardian_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION,
        variables=SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES,
    )

    assert_match_error_code(executed, API_USAGE_ERROR)
    assert "You have already used this mutation." in str(executed["errors"])


def test_submit_children_and_guardian_children_limit(user_api_client, settings):
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    variables["input"]["children"] = [
        variables["input"]["children"][0]
        for _ in range(settings.KUKKUU_MAX_NUM_OF_CHILDREN_PER_GUARDIAN + 1)
    ]

    executed = user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION,
        variables=variables,
    )

    assert_match_error_code(executed, MAX_NUMBER_OF_CHILDREN_PER_GUARDIAN_ERROR)
    assert "Too many children." in str(executed["errors"])


@pytest.mark.parametrize("guardian_email", ["INVALID_EMAIL", "", None])
def test_submit_children_and_guardian_email_validation(user_api_client, guardian_email):
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    variables["input"]["guardian"]["email"] = guardian_email

    executed = user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION, variables=variables
    )

    assert_match_error_code(executed, INVALID_EMAIL_FORMAT_ERROR)


CHILDREN_QUERY = """
query Children {
  children {
    edges {
      node {
        firstName
        lastName
        birthdate
        postalCode
        relationships {
          edges {
            node {
              type
              guardian {
                firstName
                lastName
                phoneNumber
                email
              }
            }
          }
        }
      }
    }
  }
}
"""


def test_children_query_unauthenticated(api_client):
    executed = api_client.execute(CHILDREN_QUERY)

    assert_permission_denied(executed)


def test_children_query_normal_user(snapshot, user_api_client, project):
    ChildWithGuardianFactory(
        relationship__guardian__user=user_api_client.user, project=project
    )

    executed = user_api_client.execute(CHILDREN_QUERY)

    snapshot.assert_match(executed)


def test_children_query_project_user(
    snapshot, project_user_api_client, project, another_project
):
    ChildWithGuardianFactory(
        first_name="Same project", last_name="Should be returned 1/1", project=project
    )
    ChildWithGuardianFactory(
        first_name="Another project",
        last_name="Should NOT be returned",
        project=another_project,
    )

    executed = project_user_api_client.execute(CHILDREN_QUERY)

    snapshot.assert_match(executed)


def test_children_query_project_user_and_guardian(
    snapshot, project_user_api_client, project, another_project
):
    guardian = GuardianFactory(user=project_user_api_client.user)

    ChildWithGuardianFactory(
        first_name="Own child same project",
        last_name="Should be returned 1/3",
        project=project,
        relationship__guardian=guardian,
    )
    ChildWithGuardianFactory(
        first_name="Own child another project",
        last_name="Should be returned 2/3",
        project=project,
        relationship__guardian=guardian,
    )
    ChildWithGuardianFactory(
        first_name="Not own child same project",
        last_name="Should be returned 3/3",
        project=project,
    )
    ChildWithGuardianFactory(
        first_name="Not own child another project",
        last_name="Should NOT be returned",
        project=another_project,
    )

    executed = project_user_api_client.execute(CHILDREN_QUERY)

    snapshot.assert_match(executed)


CHILDREN_FILTER_QUERY = """
query Children($projectId: ID!) {
  children(projectId: $projectId) {
    edges {
      node {
        firstName
        lastName
      }
    }
  }
}
"""


def test_children_project_filter(
    snapshot, two_project_user_api_client, project, another_project
):
    ChildWithGuardianFactory(
        first_name="Only I", last_name="Should be returned", project=project
    )
    ChildWithGuardianFactory(
        first_name="I certainly",
        last_name="Should NOT be returned",
        project=another_project,
    )
    variables = {"projectId": get_global_id(project)}

    executed = two_project_user_api_client.execute(
        CHILDREN_FILTER_QUERY, variables=variables
    )

    snapshot.assert_match(executed)


CHILD_QUERY = """
query Child($id: ID!) {
  child(id: $id) {
    firstName
    lastName
    birthdate
    postalCode
    relationships {
      edges {
        node {
          type
          guardian {
            firstName
            lastName
            phoneNumber
            email
          }
        }
      }
    }
  }
}
"""

CHILD_EVENTS_QUERY = """
query Child($id: ID!) {
  child(id: $id) {
    availableEvents{
      edges{
        node{
          createdAt
          occurrences{
            edges{
              node{
                remainingCapacity
              }
            }
          }
        }
      }
    }
    pastEvents{
      edges{
        node{
          createdAt
          name
          occurrences{
            edges{
              node{
                remainingCapacity
              }
            }
          }
        }
      }
    }
    occurrences {
      edges {
        node {
          time
        }
      }
    }
  }
}
"""


def test_child_query_unauthenticated(snapshot, api_client, child_with_random_guardian):
    variables = {"id": to_global_id("ChildNode", child_with_random_guardian.id)}

    executed = api_client.execute(CHILD_QUERY, variables=variables)

    assert_permission_denied(executed)


def test_child_query(snapshot, user_api_client, project):
    child = ChildWithGuardianFactory(
        relationship__guardian__user=user_api_client.user, project=project
    )
    variables = {"id": to_global_id("ChildNode", child.id)}

    executed = user_api_client.execute(CHILD_QUERY, variables=variables)

    snapshot.assert_match(executed)


def test_child_query_not_own_child(user_api_client, child_with_random_guardian):
    variables = {"id": to_global_id("ChildNode", child_with_random_guardian.id)}

    executed = user_api_client.execute(CHILD_QUERY, variables=variables)

    assert executed["data"]["child"] is None


def test_child_query_not_own_child_project_user(
    snapshot, project_user_api_client, child_with_random_guardian
):
    variables = {"id": to_global_id("ChildNode", child_with_random_guardian.id)}

    executed = project_user_api_client.execute(CHILD_QUERY, variables=variables)

    snapshot.assert_match(executed)


ADD_CHILD_MUTATION = """
mutation AddChild($input: AddChildMutationInput!) {
  addChild(input: $input) {
    child {
      firstName
      lastName
      birthdate
      postalCode
    }
  }
}
"""

ADD_CHILD_VARIABLES = {
    "input": {
        "firstName": "Pekka",
        "lastName": "Perälä",
        "birthdate": "2020-11-11",
        "postalCode": "00820",
        "relationship": {"type": "PARENT"},
    }
}


def test_add_child_mutation(snapshot, guardian_api_client):
    executed = guardian_api_client.execute(
        ADD_CHILD_MUTATION, variables=ADD_CHILD_VARIABLES
    )

    snapshot.assert_match(executed)

    child = Child.objects.last()
    assert_child_matches_data(child, ADD_CHILD_VARIABLES["input"])

    relationship = Relationship.objects.get(
        guardian=guardian_api_client.user.guardian, child=child
    )
    assert_relationship_matches_data(
        relationship, ADD_CHILD_VARIABLES["input"]["relationship"]
    )


def test_add_child_mutation_birthdate_required(guardian_api_client):
    variables = deepcopy(ADD_CHILD_VARIABLES)
    variables["input"].pop("birthdate")
    executed = guardian_api_client.execute(ADD_CHILD_MUTATION, variables=variables)

    # GraphQL input error for missing required fields
    assert_match_error_code(executed, GENERAL_ERROR)
    assert "birthdate" in str(executed["errors"])
    assert Child.objects.count() == 0


def test_add_child_mutation_postal_code_validation(
    guardian_api_client, invalid_postal_code
):
    variables = deepcopy(ADD_CHILD_VARIABLES)
    variables["input"]["postalCode"] = invalid_postal_code

    executed = guardian_api_client.execute(ADD_CHILD_MUTATION, variables=variables)

    assert_match_error_code(executed, DATA_VALIDATION_ERROR)
    assert "Postal code must be 5 digits" in str(executed["errors"])
    assert Child.objects.count() == 0


def test_add_child_mutation_birthdate_validation(
    guardian_api_client, illegal_birthdate
):
    variables = deepcopy(ADD_CHILD_VARIABLES)
    variables["input"]["birthdate"] = illegal_birthdate

    executed = guardian_api_client.execute(ADD_CHILD_MUTATION, variables=variables)
    assert_match_error_code(executed, DATA_VALIDATION_ERROR)
    assert "Illegal birthdate." in str(executed["errors"])


def test_add_child_mutation_requires_guardian(user_api_client):
    executed = user_api_client.execute(
        ADD_CHILD_MUTATION, variables=ADD_CHILD_VARIABLES
    )
    assert_match_error_code(executed, API_USAGE_ERROR)
    assert 'You need to use "SubmitChildrenAndGuardianMutation" first.' in str(
        executed["errors"]
    )
    assert Child.objects.count() == 0


def test_add_child_mutation_children_limit(guardian_api_client, settings, project):
    ChildWithGuardianFactory.create_batch(
        settings.KUKKUU_MAX_NUM_OF_CHILDREN_PER_GUARDIAN,
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )

    executed = guardian_api_client.execute(
        ADD_CHILD_MUTATION, variables=ADD_CHILD_VARIABLES
    )

    assert_match_error_code(executed, MAX_NUMBER_OF_CHILDREN_PER_GUARDIAN_ERROR)


UPDATE_CHILD_MUTATION = """
mutation UpdateChild($input: UpdateChildMutationInput!) {
  updateChild(input: $input) {
    child {
      firstName
      lastName
      birthdate
      postalCode
    }
  }
}
"""

UPDATE_CHILD_VARIABLES = {
    "input": {
        # "id" needs to be added when actually using these in the mutation
        "firstName": "Matti",
        "lastName": "Mainio",
        "birthdate": "2020-01-01",
        "postalCode": "00840",
        "relationship": {"type": "OTHER_GUARDIAN"},
    }
}


def test_update_child_mutation(snapshot, guardian_api_client, child_with_user_guardian):
    variables = deepcopy(UPDATE_CHILD_VARIABLES)
    variables["input"]["id"] = to_global_id("ChildNode", child_with_user_guardian.id)

    executed = guardian_api_client.execute(UPDATE_CHILD_MUTATION, variables=variables)

    snapshot.assert_match(executed)

    child_with_user_guardian.refresh_from_db()
    assert_child_matches_data(child_with_user_guardian, variables["input"])

    relationship = Relationship.objects.get(
        guardian=guardian_api_client.user.guardian, child=child_with_user_guardian
    )
    assert_relationship_matches_data(relationship, variables["input"]["relationship"])


def test_update_child_mutation_should_have_no_required_fields(
    snapshot, guardian_api_client, child_with_user_guardian
):
    variables = {
        "input": {"id": to_global_id("ChildNode", child_with_user_guardian.id)}
    }

    executed = guardian_api_client.execute(UPDATE_CHILD_MUTATION, variables=variables)

    snapshot.assert_match(executed)


def test_update_child_mutation_wrong_user(user_api_client, child_with_random_guardian):
    variables = deepcopy(UPDATE_CHILD_VARIABLES)
    variables["input"]["id"] = to_global_id("ChildNode", child_with_random_guardian.id)

    executed = user_api_client.execute(UPDATE_CHILD_MUTATION, variables=variables)

    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)


def test_update_child_mutation_postal_code_validation(
    guardian_api_client, invalid_postal_code, child_with_user_guardian
):
    variables = deepcopy(UPDATE_CHILD_VARIABLES)
    variables["input"]["id"] = to_global_id("ChildNode", child_with_user_guardian.id)
    variables["input"]["postalCode"] = invalid_postal_code

    executed = guardian_api_client.execute(UPDATE_CHILD_MUTATION, variables=variables)

    assert "Postal code must be 5 digits" in str(executed["errors"])


def test_update_child_mutation_birthdate_validation(
    guardian_api_client, illegal_birthdate, child_with_user_guardian
):
    variables = deepcopy(UPDATE_CHILD_VARIABLES)
    variables["input"]["id"] = to_global_id("ChildNode", child_with_user_guardian.id)
    variables["input"]["birthdate"] = illegal_birthdate

    executed = guardian_api_client.execute(UPDATE_CHILD_MUTATION, variables=variables)

    assert "Illegal birthdate." in str(executed["errors"])


DELETE_CHILD_MUTATION = """
mutation DeleteChild($input: DeleteChildMutationInput!) {
  deleteChild(input: $input) {__typename}
}
"""


def test_delete_child_mutation(snapshot, guardian_api_client, child_with_user_guardian):
    variables = {
        "input": {"id": to_global_id("ChildNode", child_with_user_guardian.id)}
    }

    executed = guardian_api_client.execute(DELETE_CHILD_MUTATION, variables=variables)

    snapshot.assert_match(executed)
    assert Child.objects.count() == 0


def test_delete_child_mutation_wrong_user(
    snapshot, guardian_api_client, child_with_random_guardian
):
    variables = {
        "input": {"id": to_global_id("ChildNode", child_with_random_guardian.id)}
    }

    executed = guardian_api_client.execute(DELETE_CHILD_MUTATION, variables=variables)

    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)
    assert Child.objects.count() == 1


def test_get_available_events(
    snapshot,
    guardian_api_client,
    unpublished_event,
    child_with_user_guardian,
    project,
    venue,
):
    variables = {"id": to_global_id("ChildNode", child_with_user_guardian.id)}
    next_project = ProjectFactory(year=2021)
    # Unpublished occurrences
    OccurrenceFactory(time=timezone.now(), event=unpublished_event, venue=venue)

    # Published occurrences
    occurrence = OccurrenceFactory(
        time=timezone.now(),
        event__published_at=timezone.now(),
        event__project=project,
        venue=venue,
    )
    OccurrenceFactory(
        time=timezone.now(),
        event__published_at=timezone.now(),
        event__project=project,
        venue=venue,
    )

    # Published occurrence but from another project
    OccurrenceFactory(
        time=timezone.now(),
        event__published_at=timezone.now(),
        event__project=next_project,
        venue=venue,
    )

    # Past occurrences
    OccurrenceFactory.create_batch(
        3,
        time=datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE)),
        event__project=project,
        venue=venue,
    )

    EnrolmentFactory(child=child_with_user_guardian, occurrence=occurrence)
    executed = guardian_api_client.execute(CHILD_EVENTS_QUERY, variables=variables)
    # Should only return available events from current project
    assert len(executed["data"]["child"]["availableEvents"]["edges"]) == 1
    snapshot.assert_match(executed)

    assign_perm("admin", guardian_api_client.user, project)
    executed2 = guardian_api_client.execute(CHILD_EVENTS_QUERY, variables=variables)

    # having admin rights on the project should not affect available events
    assert (
        executed2["data"]["child"]["availableEvents"]
        == executed["data"]["child"]["availableEvents"]
    )


def test_get_past_events(
    snapshot, guardian_api_client, child_with_user_guardian, project, venue
):
    variables = {"id": to_global_id("ChildNode", child_with_user_guardian.id)}

    past = timezone.now() - timedelta(
        minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY + 1
    )
    not_enough_past = timezone.now() - timedelta(
        minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY - 1
    )
    future = timezone.now() + timedelta(minutes=1)

    # Enrolled occurrence in the past, event should be visible
    event = EventFactory(
        published_at=timezone.now(),
        project=project,
        name="enrolled occurrence in the past",
    )
    OccurrenceFactory(time=future, event=event, venue=venue)
    the_past_occurrence = OccurrenceFactory(time=past, event=event, venue=venue)
    EnrolmentFactory(child=child_with_user_guardian, occurrence=the_past_occurrence)

    # Enrolled occurrence in the past but not enough, event should NOT be visible
    event_2 = EventFactory(
        published_at=timezone.now(),
        project=project,
        name="enrolled occurrence in the past but not enough",
    )
    OccurrenceFactory(time=future, event=event_2, venue=venue)
    the_not_so_past_occurrence = OccurrenceFactory(
        time=not_enough_past, event=event_2, venue=venue
    )
    EnrolmentFactory(
        child=child_with_user_guardian, occurrence=the_not_so_past_occurrence
    )

    # Event without an enrolment in the past, should NOT be visible
    event_3 = EventFactory(
        published_at=timezone.now(),
        project=project,
        name="unenrolled event in the past",
    )
    OccurrenceFactory(time=past, event=event_3, venue=venue)
    OccurrenceFactory(time=not_enough_past, event=event_3, venue=venue)

    executed = guardian_api_client.execute(CHILD_EVENTS_QUERY, variables=variables)
    snapshot.assert_match(executed)

    assign_perm("admin", guardian_api_client.user, project)
    executed2 = guardian_api_client.execute(CHILD_EVENTS_QUERY, variables=variables)

    # having admin rights on the project should not affect past events
    assert (
        executed2["data"]["child"]["pastEvents"]
        == executed["data"]["child"]["pastEvents"]
    )


CHILDREN_PAGINATION_QUERY = """
query Children($projectId: ID!, $limit: Int, $offset: Int, $after: String, $first: Int) {
  children(projectId: $projectId, limit: $limit, offset: $offset, after: $after, first: $first) {
    edges {
      node {
        lastName
      }
    }
  }
}
"""  # noqa: E501


def test_children_cursor_and_offset_pagination_cannot_be_combined(
    project_user_api_client, project
):
    variables = {
        "projectId": get_global_id(project),
        "limit": 2,
        "offset": 2,
        "after": "foo",
        "first": 2,
    }

    executed = project_user_api_client.execute(
        CHILDREN_PAGINATION_QUERY,
        variables=variables,
    )

    assert_match_error_code(executed, API_USAGE_ERROR)


@pytest.mark.parametrize(
    "limit, offset",
    ((None, 2), (2, None), (2, 2), (10, None), (None, 5)),
)
def test_children_offset_pagination(
    snapshot, project_user_api_client, project, limit, offset
):
    for i in range(5):
        ChildWithGuardianFactory(last_name=i, project=project)
    variables = {"projectId": get_global_id(project), "limit": limit, "offset": offset}

    executed = project_user_api_client.execute(
        CHILDREN_PAGINATION_QUERY,
        variables=variables,
    )

    snapshot.assert_match(executed)


@pytest.mark.parametrize("pagination", (None, "limit", "first"))
def test_children_total_count(
    snapshot, project_user_api_client, project, another_project, pagination
):
    ChildWithGuardianFactory.create_batch(5, project=project)
    ChildWithGuardianFactory.create_batch(5, project=another_project)
    variables = {"projectId": get_global_id(project)}
    if pagination:
        variables.update({pagination: 2})

    executed = project_user_api_client.execute(
        """
query Children($projectId: ID!, $limit: Int, $first: Int) {
  children(projectId: $projectId, limit: $limit, first: $first) {
    count
  }
}""",
        variables=variables,
    )

    snapshot.assert_match(executed)


def test_children_query_ordering(snapshot, project, project_user_api_client):
    with freeze_time("2020-12-12"):
        ChildWithGuardianFactory(
            first_name="Alpha", last_name="Virtanen", project=project
        )
        ChildWithGuardianFactory(
            first_name="Beta", last_name="Virtanen", project=project
        )
        ChildWithGuardianFactory(
            first_name="Beta", last_name="Korhonen", project=project
        )
        ChildWithGuardianFactory(first_name="Beta", last_name="", project=project)
        ChildWithGuardianFactory(first_name="Alpha", last_name="", project=project)
        ChildWithGuardianFactory(first_name="", last_name="Virtanen", project=project)
        ChildWithGuardianFactory(first_name="", last_name="Korhonen", project=project)
        ChildWithGuardianFactory(first_name="", last_name="", project=project)
    with freeze_time("2020-11-11"):
        ChildWithGuardianFactory(first_name="", last_name="", project=project)
        ChildWithGuardianFactory(first_name="", last_name="Korhonen", project=project)

    executed = project_user_api_client.execute(
        """
    query Children {
      children {
        edges {
          node {
            createdAt
            firstName
            lastName
          }
        }
      }
    }
    """
    )

    snapshot.assert_match(executed)


CHILD_AVAILABLE_EVENTS_AND_EVENT_GROUPS_QUERY = """
query Child($id: ID!) {
  child(id: $id) {
    availableEventsAndEventGroups{
      edges {
        node {
          ... on EventNode {
            name
            __typename
          }
          ... on EventGroupNode {
            name
            __typename
          }
        }
      }
    }
  }
}
"""


def test_available_events_and_event_groups(
    snapshot,
    guardian_api_client,
    child_with_user_guardian,
    future,
    past,
    project,
    another_project,
):
    # the following should NOT be returned

    EventFactory(published_at=now())  # event without occurrences
    OccurrenceFactory(time=future)  # unpublished event
    EnrolmentFactory(
        child=child_with_user_guardian,
        occurrence=OccurrenceFactory(time=future, event=EventFactory()),
    )  # enrolled event
    OccurrenceFactory(event__published_at=now(), time=past)  # event in past
    OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__project=another_project,
    )  # event from another project
    EventGroupFactory(published_at=now())  # empty event group
    EventFactory(
        event_group=EventGroupFactory(published_at=now()), published_at=now()
    )  # event group without occurrences
    OccurrenceFactory(
        time=future, event__event_group=EventGroupFactory()
    )  # unpublished event group
    event_group = EventGroupFactory(published_at=now())
    event_group_occurrences = OccurrenceFactory.create_batch(
        2,
        time=timezone.now(),
        event__published_at=now(),
        event__event_group=event_group,
    )
    EnrolmentFactory(
        child=child_with_user_guardian, occurrence=event_group_occurrences[0]
    )  # event group with one of two events enrolled
    OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__project=another_project,
        event__event_group=EventGroupFactory(
            published_at=now(), project=another_project
        ),
    )  # event group from another project

    # the following should be returned

    OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__event_group=EventGroupFactory(
            name="this should be the third", published_at=now() + timedelta(minutes=2)
        ),
    )
    OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__event_group=EventGroupFactory(
            name="this should be the first", published_at=now() + timedelta(minutes=4)
        ),
    )
    OccurrenceFactory(
        time=future,
        event=EventFactory(
            published_at=now() + timedelta(minutes=3), name="this should be the second"
        ),
    )
    OccurrenceFactory(
        time=future,
        event=EventFactory(
            published_at=now() + timedelta(minutes=1), name="this should be the fourth"
        ),
    )

    variables = {"id": get_global_id(child_with_user_guardian)}

    executed = guardian_api_client.execute(
        CHILD_AVAILABLE_EVENTS_AND_EVENT_GROUPS_QUERY, variables=variables
    )

    snapshot.assert_match(executed)

    assign_perm("admin", guardian_api_client.user, project)
    executed2 = guardian_api_client.execute(
        CHILD_AVAILABLE_EVENTS_AND_EVENT_GROUPS_QUERY, variables=variables
    )

    # having admin rights on the project should not affect available events
    assert (
        executed2["data"]["child"]["availableEventsAndEventGroups"]
        == executed["data"]["child"]["availableEventsAndEventGroups"]
    )
