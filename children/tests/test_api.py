from copy import deepcopy
from datetime import datetime, timedelta

import pytest
import pytz
from auditlog.context import disable_auditlog
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import localtime, now
from freezegun import freeze_time
from graphene.utils.str_converters import to_snake_case
from graphql_relay import offset_to_cursor, to_global_id
from guardian.shortcuts import assign_perm

from children.factories import ChildWithGuardianFactory
from children.tests.mutations import (
    ADD_CHILD_MUTATION,
    DELETE_CHILD_MUTATION,
    SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION,
    UPDATE_CHILD_MUTATION,
    UPDATE_CHILD_NOTES_MUTATION,
    UPDATE_CHILD_NOTES_MUTATION_TEMPLATE,
)
from children.tests.queries import (
    CHILD_ACTIVE_INTERNAL_AND_TICKETMASTER_ENROLMENTS_QUERY,
    CHILD_AVAILABLE_EVENTS_AND_EVENT_GROUPS_QUERY,
    CHILD_ENROLMENT_COUNT_QUERY,
    CHILD_EVENTS_QUERY,
    CHILD_NOTES_QUERY,
    CHILD_NOTES_QUERY_TEMPLATE,
    CHILD_NOTES_QUERY_WITHOUT_ID_PARAMETER,
    CHILD_PAST_EVENTS_QUERY,
    CHILD_QUERY,
    CHILD_UPCOMING_EVENTS_AND_EVENT_GROUPS_QUERY,
    CHILDREN_FILTER_QUERY,
    CHILDREN_PAGINATION_QUERY,
    CHILDREN_QUERY,
)
from common.tests.utils import (
    assert_error_message,
    assert_general_error,
    assert_match_error_code,
    assert_permission_denied,
)
from common.utils import get_global_id, get_node_id_from_global_id
from events.factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    OccurrenceFactory,
    RandomExternalTicketSystemEventFactory,
    TicketSystemPasswordFactory,
)
from events.models import Event
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
from projects.models import ProjectPermission
from users.factories import GuardianFactory
from users.models import Guardian

from ..models import Child, Relationship

CHILD_MODEL_FIELDS = [field.name for field in Child._meta.get_fields()]

CHILD_MODEL_FIELDS_WITHOUT_ID_OR_NOTES = [
    field for field in CHILD_MODEL_FIELDS if field not in ["id", "notes"]
]

EXTRA_CHILD_NOTES_FIELDS = CHILD_MODEL_FIELDS_WITHOUT_ID_OR_NOTES + ["inexistent_field"]


@pytest.fixture(params=EXTRA_CHILD_NOTES_FIELDS)
def extra_child_notes_field_name(request):
    """
    Field names that can't be queried in the child notes query.
    """
    return request.param


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture(params=("1234x", ""))
def invalid_postal_code(request):
    return request.param


@pytest.fixture(params=[0, 1])
def illegal_birthyear(request):
    # these dates cannot be set to params directly because now() would not be
    # the faked one
    return (
        2019,  # wrong year
        localtime(now()).year + 1,  # in the future
    )[request.param]


def assert_child_matches_data(child_obj, child_data):
    child_data = child_data or {}
    for field_name in ("name", "birthyear", "postalCode"):
        if field_name in child_data:
            value = getattr(child_obj, to_snake_case(field_name))
            assert (
                value
                if field_name == "birthyear"
                else str(value) == child_data[field_name]
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
            get_node_id_from_global_id(lang, "LanguageNode")
            for lang in guardian_data["languagesSpokenAtHome"]
        ]
        assert set(guardian_obj.languages_spoken_at_home.all()) == set(
            Language.objects.filter(id__in=language_ids)
        )


CHILDREN_DATA = [
    {
        "name": "Matti",
        "birthyear": 2020,
        "postalCode": "00840",
        "relationship": {"type": "OTHER_GUARDIAN"},
    },
    {
        "name": "Jussi",
        "birthyear": 2020,
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


def test_submit_children_and_guardian(snapshot, user_api_client, languages, project):
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
        Child.objects.order_by("birthyear"), variables["input"]["children"]
    ):
        assert_child_matches_data(child, child_data)
        relationship = Relationship.objects.get(guardian=guardian, child=child)
        assert_relationship_matches_data(relationship, child_data.get("relationship"))
        assert child.notes == ""


def test_submit_children_and_guardian_without_email(snapshot, user_api_client, project):
    """
    Test that guardian email is set to user's email,
    if guardian email is not provided.
    """
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    assert "email" not in variables["input"]["guardian"]

    executed = user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION, variables=variables
    )

    snapshot.assert_match(executed)

    guardian = Guardian.objects.last()
    # Guardian's email uses the user's email as a fallback
    variables["input"]["guardian"]["email"] = guardian.user.email
    assert_guardian_matches_data(guardian, variables["input"]["guardian"])


@pytest.mark.parametrize("guardian_email", [None, ""])
def test_submit_children_and_guardian_with_falsy_email(
    snapshot, user_api_client, project, guardian_email
):
    """
    Test that guardian email is set to user's email,
    if a falsy guardian email is provided.
    """
    assert not guardian_email
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    variables["input"]["guardian"]["email"] = guardian_email

    executed = user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION, variables=variables
    )

    snapshot.assert_match(executed)

    guardian = Guardian.objects.last()
    assert guardian.user.email
    variables["input"]["guardian"]["email"] = guardian.user.email
    assert_guardian_matches_data(guardian, variables["input"]["guardian"])


def test_submit_children_and_guardian_with_non_user_email(user_api_client, project):
    """
    Test that guardian email input is rejected,
    if it's non-empty and differs from user's email.
    """
    user = user_api_client.user
    assert user.email
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    variables["input"]["guardian"]["email"] = "updated_email@example.com"
    assert variables["input"]["guardian"]["email"] != user.email

    executed = user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION, variables=variables
    )

    assert_match_error_code(executed, API_USAGE_ERROR)
    assert_error_message(executed, "Guardian email must be the same as user email.")

    assert not Guardian.objects.exists()


def test_submit_children_and_guardian_with_user_email(
    snapshot, user_api_client, project
):
    """
    Test that guardian email input is accepted, if it's same as user's email.
    """
    user = user_api_client.user
    assert user.email
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    variables["input"]["guardian"]["email"] = user.email

    executed = user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION, variables=variables
    )

    snapshot.assert_match(executed)

    assert Guardian.objects.exists()
    guardian = Guardian.objects.last()
    assert_guardian_matches_data(guardian, variables["input"]["guardian"])


def test_submit_children_and_guardian_one_child_required(user_api_client):
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


def test_submit_children_and_guardian_birthyear_validation(
    user_api_client, illegal_birthyear
):
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    variables["input"]["children"][0]["birthyear"] = illegal_birthyear

    executed = user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION, variables=variables
    )

    assert_match_error_code(executed, DATA_VALIDATION_ERROR)
    assert "Illegal birthyear." in str(executed["errors"])


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


@pytest.mark.parametrize("guardian_email", ["INVALID_EMAIL", " ", "@"])
def test_submit_children_and_guardian_email_validation(user_api_client, guardian_email):
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    variables["input"]["guardian"]["email"] = guardian_email

    executed = user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION, variables=variables
    )

    assert_match_error_code(executed, INVALID_EMAIL_FORMAT_ERROR)


def test_children_query_unauthenticated(api_client):
    executed = api_client.execute(CHILDREN_QUERY)

    assert_permission_denied(executed)


def test_children_query_normal_user(user_api_client, project):
    ChildWithGuardianFactory(
        relationship__guardian__user=user_api_client.user, project=project
    )

    executed = user_api_client.execute(CHILDREN_QUERY)

    assert_permission_denied(executed)


def test_children_query_project_user(project_user_api_client):
    executed = project_user_api_client.execute(CHILDREN_QUERY)

    assert_permission_denied(executed)


def test_children_query_project_user_with_global_view_families_perm(
    snapshot, project_user_api_client, project, another_project
):
    ChildWithGuardianFactory(
        name="Same project - Should be returned 1/1", project=project
    )
    ChildWithGuardianFactory(
        name="Another project - Should NOT be returned",
        project=another_project,
    )

    # Give user global permission to view families
    assign_perm(
        ProjectPermission.VIEW_FAMILIES.permission_name, project_user_api_client.user
    )

    executed = project_user_api_client.execute(CHILDREN_QUERY)

    snapshot.assert_match(executed)


def test_children_query_project_user_no_view_families_perm(
    project_user_no_view_families_perm_api_client, project
):
    executed = project_user_no_view_families_perm_api_client.execute(CHILDREN_QUERY)
    assert_permission_denied(executed)


def test_children_project_filter(
    snapshot, two_project_user_api_client, project, another_project
):
    ChildWithGuardianFactory(name="Only I should be returned", project=project)
    ChildWithGuardianFactory(
        name="I certainly should NOT be returned",
        project=another_project,
    )
    variables = {"projectId": get_global_id(project)}

    executed = two_project_user_api_client.execute(
        CHILDREN_FILTER_QUERY, variables=variables
    )

    snapshot.assert_match(executed)


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


def test_child_query_not_own_child_project_user_no_view_families_perm(
    project_user_no_view_families_perm_api_client, project
):
    """
    Test that project user without view families permission sees others' child info
    using Child query, but the guardian's email and phone number are empty.
    """
    child = ChildWithGuardianFactory(
        name="Test child name",
        birthyear=2020,
        postal_code="00100",
        relationship__type=Relationship.PARENT,
        relationship__guardian=GuardianFactory(
            first_name="Test first name",
            last_name="Test last name",
            email="test@example.org",
            phone_number="123456789",
        ),
        project=project,
    )

    variables = {"id": to_global_id("ChildNode", child.id)}

    executed = project_user_no_view_families_perm_api_client.execute(
        CHILD_QUERY, variables=variables
    )

    assert executed == {
        "data": {
            "child": {
                "name": "Test child name",
                "birthyear": 2020,
                "postalCode": "00100",
                "relationships": {
                    "edges": [
                        {
                            "node": {
                                "type": "PARENT",
                                "guardian": {
                                    "firstName": "Test first name",
                                    "lastName": "Test last name",
                                    # Guardian's contact info should be empty
                                    "email": "",
                                    "phoneNumber": "",
                                },
                            }
                        }
                    ]
                },
            }
        }
    }


def test_child_query_own_child_project_user_no_view_families_perm(
    project_user_no_view_families_perm_api_client, project
):
    """
    Test that project user without view families permission sees their own child
    using Child query, and the guardian's email and phone number are visible too.
    """
    user = project_user_no_view_families_perm_api_client.user
    child = ChildWithGuardianFactory(
        name="Test child name",
        birthyear=2020,
        postal_code="00100",
        relationship__type=Relationship.PARENT,
        relationship__guardian=GuardianFactory(
            user=user,
            first_name="Test first name",
            last_name="Test last name",
            email="test@example.org",
            phone_number="123456789",
        ),
        project=project,
    )

    variables = {"id": to_global_id("ChildNode", child.id)}

    executed = project_user_no_view_families_perm_api_client.execute(
        CHILD_QUERY, variables=variables
    )

    assert executed == {
        "data": {
            "child": {
                "name": "Test child name",
                "birthyear": 2020,
                "postalCode": "00100",
                "relationships": {
                    "edges": [
                        {
                            "node": {
                                "type": "PARENT",
                                "guardian": {
                                    "firstName": "Test first name",
                                    "lastName": "Test last name",
                                    # Guardian's contact info should be visible
                                    "email": "test@example.org",
                                    "phoneNumber": "123456789",
                                },
                            }
                        }
                    ]
                },
            }
        }
    }


ADD_CHILD_VARIABLES = {
    "input": {
        "name": "Pekka",
        "birthyear": 2020,
        "postalCode": "00820",
        "relationship": {"type": "PARENT"},
    }
}


def test_add_child_mutation(snapshot, guardian_api_client, project):
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
    assert child.notes == ""


def test_add_child_mutation_birthyear_required(guardian_api_client):
    variables = deepcopy(ADD_CHILD_VARIABLES)
    variables["input"].pop("birthyear")
    executed = guardian_api_client.execute(ADD_CHILD_MUTATION, variables=variables)

    # GraphQL input error for missing required fields
    assert_match_error_code(executed, GENERAL_ERROR)
    assert "birthyear" in str(executed["errors"])
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


def test_add_child_mutation_birthyear_validation(
    guardian_api_client, illegal_birthyear
):
    variables = deepcopy(ADD_CHILD_VARIABLES)
    variables["input"]["birthyear"] = illegal_birthyear

    executed = guardian_api_client.execute(ADD_CHILD_MUTATION, variables=variables)
    assert_match_error_code(executed, DATA_VALIDATION_ERROR)
    assert "Illegal birthyear." in str(executed["errors"])


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


UPDATE_CHILD_VARIABLES = {
    "input": {
        # "id" needs to be added when actually using these in the mutation
        "name": "Matti",
        "postalCode": "00840",
        "relationship": {"type": "OTHER_GUARDIAN"},
    }
}


def test_update_child_mutation(snapshot, guardian_api_client, child_with_user_guardian):
    original_notes = child_with_user_guardian.notes
    original_birthyear = child_with_user_guardian.birthyear
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
    assert child_with_user_guardian.birthyear == original_birthyear
    assert child_with_user_guardian.notes == original_notes


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


def test_update_child_mutation_birthdate_validation_illegal_date(
    guardian_api_client, illegal_birthyear, child_with_user_guardian
):
    variables = deepcopy(UPDATE_CHILD_VARIABLES)
    variables["input"]["id"] = to_global_id("ChildNode", child_with_user_guardian.id)
    variables["input"]["birthyear"] = illegal_birthyear

    executed = guardian_api_client.execute(UPDATE_CHILD_MUTATION, variables=variables)

    assert "GENERAL_ERROR" in str(executed["errors"])


def test_update_child_mutation_birthdate_not_mutable_on_update(
    guardian_api_client, child_with_user_guardian
):
    variables = deepcopy(UPDATE_CHILD_VARIABLES)
    variables["input"]["id"] = to_global_id("ChildNode", child_with_user_guardian.id)
    variables["input"]["birthdate"] = "2020-01-01"

    executed = guardian_api_client.execute(UPDATE_CHILD_MUTATION, variables=variables)

    assert "GENERAL_ERROR" in str(executed["errors"])


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


def test_update_child_notes_mutation_unauthenticated(
    api_client, child_with_random_guardian
):
    variables = {
        "input": {
            "childId": to_global_id("ChildNode", child_with_random_guardian.id),
            "notes": "Test notes",
        }
    }

    executed = api_client.execute(UPDATE_CHILD_NOTES_MUTATION, variables=variables)

    assert_permission_denied(executed)


def test_update_child_notes_mutation_wrong_user(
    guardian_api_client, child_with_random_guardian
):
    """
    Test that UpdateChildNotes mutation can not find the child,
    if the user is not a guardian of the child.
    """
    variables = {
        "input": {
            "childId": to_global_id("ChildNode", child_with_random_guardian.id),
            "notes": "Test notes",
        }
    }

    executed = guardian_api_client.execute(
        UPDATE_CHILD_NOTES_MUTATION, variables=variables
    )

    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)
    assert_error_message(executed, "Child matching query does not exist.")


@pytest.mark.parametrize("orig_notes", ["", "Notes", "Alternative notes"])
def test_update_child_notes_mutation(
    guardian_api_client, child_with_user_guardian, orig_notes
):
    """
    Test that UpdateChildNotes mutation updates the child's notes and nothing else.

    NOTE: Using shallow equality check when checking that other than the "notes"
          field didn't change, deep equality check would be more comprehensive.
    """
    child = child_with_user_guardian  # alias for brevity

    # Set up notes to a known value
    child.notes = orig_notes
    child.save()
    child.refresh_from_db()

    # Save original values
    orig_child_id = child.id
    orig_name = child.name
    orig_birthyear = child.birthyear
    orig_postal_code = child.postal_code
    orig_guardian_ids = sorted(child.guardians.values_list("id", flat=True))
    orig_languages_spoken_at_home_ids = sorted(
        child.languages_spoken_at_home.values_list("id", flat=True)
    )
    orig_project_id = child.project_id

    variables = {
        "input": {
            "childId": to_global_id("ChildNode", child.id),
            "notes": "Updated child notes",
        }
    }

    assert child.notes == orig_notes

    executed = guardian_api_client.execute(
        UPDATE_CHILD_NOTES_MUTATION, variables=variables
    )

    child.refresh_from_db()
    assert child.notes == "Updated child notes"

    assert executed == {
        "data": {
            "updateChildNotes": {
                "childNotes": {
                    "childId": str(orig_child_id),
                    "notes": "Updated child notes",
                }
            }
        }
    }

    # Check that fields stayed the same
    new_guardian_ids = sorted(child.guardians.values_list("id", flat=True))
    new_languages_spoken_at_home_ids = sorted(
        child.languages_spoken_at_home.values_list("id", flat=True)
    )
    assert child.name == orig_name
    assert child.birthyear == orig_birthyear
    assert child.postal_code == orig_postal_code
    assert new_guardian_ids == orig_guardian_ids
    assert new_languages_spoken_at_home_ids == orig_languages_spoken_at_home_ids
    assert child.project_id == orig_project_id


def test_update_child_notes_mutation_no_extra_fields(
    guardian_api_client, child_with_user_guardian, extra_child_notes_field_name
):
    """
    Test that UpdateChildNotes mutation gives an error, if extra fields are requested.
    """
    extra_field_name = extra_child_notes_field_name  # alias for brevity
    variables = {
        "input": {
            "childId": to_global_id("ChildNode", child_with_user_guardian.id),
            "notes": "Updated child notes",
        }
    }

    executed = guardian_api_client.execute(
        UPDATE_CHILD_NOTES_MUTATION_TEMPLATE % {"extra_field_name": extra_field_name},
        variables=variables,
    )

    assert_general_error(executed)
    assert_error_message(
        executed, f"Cannot query field '{extra_field_name}' on type 'ChildNotesNode'."
    )


def test_child_notes_query_unauthenticated(api_client, child_with_random_guardian):
    """
    Test that ChildNotes query gives permission denied error,
    if the user is not authenticated.
    """
    variables = {"id": to_global_id("ChildNode", child_with_random_guardian.id)}

    executed = api_client.execute(CHILD_NOTES_QUERY, variables=variables)

    assert_permission_denied(executed)


@pytest.mark.parametrize("orig_notes", ["", "Notes", "Alternative notes"])
def test_child_notes_query(user_api_client, project, orig_notes):
    """
    Test that ChildNotes query returns the child's ID and notes,
    if the user is a guardian of the child.
    """
    child = ChildWithGuardianFactory(
        relationship__guardian__user=user_api_client.user,
        project=project,
        notes=orig_notes,
    )
    variables = {"id": to_global_id("ChildNode", child.id)}

    executed = user_api_client.execute(CHILD_NOTES_QUERY, variables=variables)

    assert executed == {
        "data": {
            "childNotes": {
                "childId": str(child.id),
                "notes": orig_notes,
            }
        }
    }


def test_child_notes_query_with_incorrect_id_type(
    user_api_client, child_with_random_guardian
):
    """
    Test that ChildNotes query gives API usage error, if ID is of incorrect type.
    """
    variables = {"id": to_global_id("ChildNotesNode", child_with_random_guardian.id)}

    executed = user_api_client.execute(CHILD_NOTES_QUERY, variables=variables)

    assert_match_error_code(executed, API_USAGE_ERROR)
    assert_error_message(
        executed,
        "childNotes must be queried using ChildNode type ID, "
        + "was queried with ChildNotesNode type ID",
    )


def test_child_notes_query_with_plain_id(user_api_client, child_with_random_guardian):
    """
    Test that ChildNotes query gives general error, if using plain UUID as ID.
    """
    variables = {"id": child_with_random_guardian.id}

    executed = user_api_client.execute(CHILD_NOTES_QUERY, variables=variables)

    assert_match_error_code(executed, GENERAL_ERROR)
    assert_error_message(
        executed,
        "Variable '$id' got invalid value <UUID instance>; "
        + "ID cannot represent value: <UUID instance>",
    )


@pytest.mark.parametrize("input_id", ["123", "ChildNode:123", 123])
def test_child_notes_query_with_incorrect_id(
    user_api_client, child_with_random_guardian, input_id
):
    """
    Test that ChildNotes query gives API usage error, if using incorrect ID.
    """
    variables = {"id": input_id}

    executed = user_api_client.execute(CHILD_NOTES_QUERY, variables=variables)

    assert_match_error_code(executed, API_USAGE_ERROR)
    assert_error_message(
        executed,
        "childNotes must be queried using ChildNode type ID, "
        + "was queried with empty type ID",
    )


def test_child_notes_query_with_null_id(user_api_client, child_with_random_guardian):
    """
    Test that ChildNotes query gives API usage error, if id is None.
    """
    variables = {"id": None}

    executed = user_api_client.execute(CHILD_NOTES_QUERY, variables=variables)

    assert_general_error(executed)
    assert_error_message(
        executed, "Variable '$id' of non-null type 'ID!' must not be null."
    )


def test_child_notes_query_not_own_child(user_api_client, child_with_random_guardian):
    """
    Test that ChildNotes query returns None, if the user is not a guardian of the child.
    """
    variables = {"id": to_global_id("ChildNode", child_with_random_guardian.id)}

    executed = user_api_client.execute(CHILD_NOTES_QUERY, variables=variables)

    assert executed == {"data": {"childNotes": None}}


def test_child_notes_query_not_own_child_but_project_admin(
    project_user_api_client, child_with_random_guardian
):
    """
    Test that ChildNotes query returns the child's ID and notes,
    if the user is an administrator of the child's project.
    """
    assert project_user_api_client.user.has_perm(
        "admin", child_with_random_guardian.project
    )
    orig_notes = child_with_random_guardian.notes
    variables = {"id": to_global_id("ChildNode", child_with_random_guardian.id)}

    executed = project_user_api_client.execute(CHILD_NOTES_QUERY, variables=variables)

    assert executed == {
        "data": {
            "childNotes": {
                "childId": str(child_with_random_guardian.id),
                "notes": orig_notes,
            }
        }
    }


def test_child_notes_query_no_extra_fields(
    user_api_client, project, extra_child_notes_field_name
):
    """
    Test that ChildNotes query gives an error, if extra fields are requested.
    """
    extra_field_name = extra_child_notes_field_name  # alias for brevity
    child = ChildWithGuardianFactory(
        relationship__guardian__user=user_api_client.user, project=project
    )
    variables = {"id": to_global_id("ChildNode", child.id)}

    executed = user_api_client.execute(
        CHILD_NOTES_QUERY_TEMPLATE % {"extra_field_name": extra_field_name},
        variables=variables,
    )

    assert_general_error(executed)
    assert_error_message(
        executed, f"Cannot query field '{extra_field_name}' on type 'ChildNotesNode'."
    )


def test_child_notes_query_without_id_parameter_fails(
    project_user_api_client, child_with_random_guardian
):
    """
    Test that ChildNotes query gives an error, if the "id" parameter is missing.
    """
    executed = project_user_api_client.execute(CHILD_NOTES_QUERY_WITHOUT_ID_PARAMETER)
    assert_general_error(executed)
    assert_error_message(
        executed,
        "Field 'childNotes' argument 'id' of type 'ID!' is required, "
        + "but it was not provided.",
    )


@freeze_time("2021-02-02T12:00:00Z")
@pytest.mark.parametrize(
    "year_delta,expected_count",
    [(-2, 0), (-1, 1), (0, 2), (None, 2), (1, 1), (2, 0)],
)
def test_child_enrolment_count(
    guardian_api_client, child_with_user_guardian, year_delta, expected_count
):
    variables = {"id": to_global_id("ChildNode", child_with_user_guardian.id)}
    if year_delta:
        variables["year"] = timezone.now().year + year_delta

    last_year = timezone.now() - relativedelta(years=1)
    this_year = timezone.now()
    next_year = timezone.now() + relativedelta(years=1)

    last_year_occurrence = OccurrenceFactory.create(
        time=last_year, event__published_at=last_year
    )
    this_year_occurences = OccurrenceFactory.create_batch(
        2, time=this_year, event__published_at=this_year
    )
    next_year_occurrence = OccurrenceFactory.create(
        time=next_year, event__published_at=now()
    )

    for occurrence in [
        last_year_occurrence,
        *this_year_occurences,
        next_year_occurrence,
    ]:
        EnrolmentFactory(
            child=child_with_user_guardian,
            occurrence=occurrence,
        )

    executed = guardian_api_client.execute(
        CHILD_ENROLMENT_COUNT_QUERY, variables=variables
    )

    assert executed["data"]["child"]["enrolmentCount"] == expected_count


@freeze_time("2021-02-02T12:00:00Z")
@pytest.mark.parametrize(
    "year_delta,expected_count",
    [(-2, 0), (-1, 1), (0, 2), (None, 2), (1, 1), (2, 0)],
)
def test_child_enrolment_count_with_ticket_system_passwords(
    guardian_api_client, child_with_user_guardian, year_delta, expected_count
):
    variables = {"id": to_global_id("ChildNode", child_with_user_guardian.id)}
    if year_delta:
        variables["year"] = timezone.now().year + year_delta

    last_year = timezone.now() - relativedelta(years=1)
    this_year = timezone.now()
    next_year = timezone.now() + relativedelta(years=1)

    last_year_event = RandomExternalTicketSystemEventFactory.create(
        ticket_system_url="https://example.com",
        published_at=last_year,
        ticket_system_end_time=last_year,
        capacity_per_occurrence=None,
    )
    this_year_events = RandomExternalTicketSystemEventFactory.create_batch(
        2,
        ticket_system_url="https://example.com",
        published_at=this_year,
        ticket_system_end_time=this_year,
        capacity_per_occurrence=None,
    )

    next_year_event = RandomExternalTicketSystemEventFactory.create(
        ticket_system_url="https://example.com",
        published_at=next_year,
        ticket_system_end_time=next_year,
        capacity_per_occurrence=None,
    )

    for event in [
        last_year_event,
        *this_year_events,
        next_year_event,
    ]:
        TicketSystemPasswordFactory(event=event, child=child_with_user_guardian)

    executed = guardian_api_client.execute(
        CHILD_ENROLMENT_COUNT_QUERY, variables=variables
    )

    assert executed["data"]["child"]["enrolmentCount"] == expected_count


@freeze_time("2021-02-02T12:00:00Z")
@pytest.mark.parametrize("past_enrolment_count", [0, 1, 2])
def test_child_past_enrolment_count(
    guardian_api_client, child_with_user_guardian, past_enrolment_count
):
    """Number of this year's enrollments in the past."""
    variables = {"id": to_global_id("ChildNode", child_with_user_guardian.id)}

    past = timezone.now() - timedelta(hours=1)
    future = timezone.now() + timedelta(hours=1)

    for i in range(past_enrolment_count):
        EnrolmentFactory(
            child=child_with_user_guardian,
            occurrence__time=past,
            occurrence__event__published_at=past,
        )

    for i in range(2 - past_enrolment_count):
        EnrolmentFactory(
            child=child_with_user_guardian,
            occurrence__time=future,
            occurrence__event__published_at=past,
        )

    executed = guardian_api_client.execute(
        CHILD_ENROLMENT_COUNT_QUERY, variables=variables
    )

    assert executed["data"]["child"]["pastEnrolmentCount"] == past_enrolment_count


@freeze_time("2021-02-02T12:00:00Z")
@pytest.mark.parametrize("past_enrolment_count", [0, 1, 2])
def test_child_past_enrolment_count_with_ticket_system_passwords(
    guardian_api_client,
    child_with_user_guardian,
    past_enrolment_count,
):
    variables = {"id": to_global_id("ChildNode", child_with_user_guardian.id)}
    child = child_with_user_guardian

    past = timezone.now() - timedelta(hours=1)
    future = timezone.now() + timedelta(hours=1)

    for i in range(past_enrolment_count):
        # some other past event
        RandomExternalTicketSystemEventFactory(published_at=past)

        someone_else_enrolled_past_event = RandomExternalTicketSystemEventFactory(
            published_at=past
        )
        TicketSystemPasswordFactory(event=someone_else_enrolled_past_event)

        # this should be counted
        enrolled_past_event = RandomExternalTicketSystemEventFactory(
            published_at=past,
        )
        TicketSystemPasswordFactory(event=enrolled_past_event, child=child)

    for i in range(2 - past_enrolment_count):
        future_event = EventFactory(
            published_at=future,
        )
        TicketSystemPasswordFactory(event=future_event, child=child_with_user_guardian)

    executed = guardian_api_client.execute(
        CHILD_ENROLMENT_COUNT_QUERY, variables=variables
    )

    assert executed["data"]["child"]["pastEnrolmentCount"] == past_enrolment_count


def test_get_available_events(
    snapshot,
    guardian_api_client,
    unpublished_event,
    child_with_user_guardian,
    project,
    another_project,
    venue,
):
    variables = {"id": to_global_id("ChildNode", child_with_user_guardian.id)}
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
        event__project=another_project,
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
    duration_mins = 30
    past = (
        timezone.now()
        - timedelta(minutes=duration_mins)
        - timedelta(minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY + 1)
    )
    not_enough_past = (
        timezone.now()
        - timedelta(minutes=duration_mins)
        - timedelta(minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY - 1)
    )
    future = timezone.now() + timedelta(minutes=1)

    # Enrolled occurrence in the past, event should be visible
    event = EventFactory(
        published_at=timezone.now(),
        duration=duration_mins,
        project=project,
        name="enrolled occurrence in the past",
    )
    OccurrenceFactory(time=future, event=event, venue=venue)
    the_past_occurrence = OccurrenceFactory(time=past, event=event, venue=venue)
    EnrolmentFactory(child=child_with_user_guardian, occurrence=the_past_occurrence)

    # Enrolled occurrence in the past but not enough, event should NOT be visible
    event_2 = EventFactory(
        published_at=timezone.now(),
        duration=duration_mins,
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
        duration=duration_mins,
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


def test_get_past_events_including_external_ticket_system_events(
    snapshot, guardian_api_client, child_with_user_guardian, project, venue
):
    variables = {"id": to_global_id("ChildNode", child_with_user_guardian.id)}
    duration_mins = 30
    past = (
        timezone.now()
        - timedelta(minutes=duration_mins)
        - timedelta(minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY + 1)
    )
    not_enough_past = (
        timezone.now()
        - timedelta(minutes=duration_mins)
        - timedelta(minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY - 1)
    )
    future = timezone.now() + timedelta(minutes=1)
    ticket_master_event_past = timezone.now() - timedelta(minutes=1)

    # Enrolled occurrence in the past, event should be visible as the first event
    event = EventFactory(
        published_at=timezone.now(),
        duration=duration_mins,
        project=project,
        name="Expected as 1/4",
    )
    OccurrenceFactory(time=future, event=event, venue=venue)
    the_past_occurrence = OccurrenceFactory(
        time=past - timedelta(hours=3), event=event, venue=venue
    )
    EnrolmentFactory(child=child_with_user_guardian, occurrence=the_past_occurrence)

    # Enrolled occurrence in the past but not enough, event should NOT be visible
    event_2 = EventFactory(
        published_at=timezone.now(),
        duration=duration_mins,
        project=project,
        name="ERROR: enrolled occurrence in the past but not enough",
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
        duration=duration_mins,
        project=project,
        name="ERROR: unenrolled event in the past",
    )
    OccurrenceFactory(time=past, event=event_3, venue=venue)
    OccurrenceFactory(time=not_enough_past, event=event_3, venue=venue)

    # Another enrolled occurrence in the past, event should be visible as the third
    # event
    event_4 = EventFactory(
        published_at=timezone.now(),
        duration=duration_mins,
        project=project,
        name="Expected as 3/4",
    )
    OccurrenceFactory(time=future, event=event_4, venue=venue)
    the_past_occurrence_2 = OccurrenceFactory(
        time=past - timedelta(hours=1), event=event_4, venue=venue
    )
    EnrolmentFactory(child=child_with_user_guardian, occurrence=the_past_occurrence_2)

    # Enrolled Ticketmaster event in the past, should be visible as the second event
    ticketmaster_event_1 = RandomExternalTicketSystemEventFactory(
        published_at=timezone.now(),
        name="Expected as 2/4",
        ticket_system_end_time=ticket_master_event_past - timedelta(hours=2),
    )
    TicketSystemPasswordFactory(
        event=ticketmaster_event_1, child=child_with_user_guardian
    )

    # Enrolled Ticketmaster event in the future, event should NOT be
    # visible
    ticketmaster_event_2 = RandomExternalTicketSystemEventFactory(
        published_at=timezone.now(),
        name="ERROR: enrolled Ticketmaster event in the future",
        ticket_system_end_time=future,
    )
    TicketSystemPasswordFactory(
        event=ticketmaster_event_2, child=child_with_user_guardian
    )

    # Unenrolled Ticketmaster event in the past, event should NOT be visible
    ticketmaster_event_3 = RandomExternalTicketSystemEventFactory(  # noqa
        published_at=timezone.now(),
        name="ERROR: unenrolled Ticketmaster event in the past",
        ticket_system_end_time=ticket_master_event_past,
    )

    # Another enrolled Ticketmaster event in the past, should be visible as the fourth
    # event
    ticketmaster_event_4 = RandomExternalTicketSystemEventFactory(
        published_at=timezone.now(),
        name="Expected as 4/4",
        ticket_system_end_time=ticket_master_event_past,
    )
    TicketSystemPasswordFactory(
        event=ticketmaster_event_4, child=child_with_user_guardian
    )

    executed = guardian_api_client.execute(CHILD_PAST_EVENTS_QUERY, variables=variables)
    assert len(executed["data"]["child"]["pastEvents"]["edges"]) == 4
    snapshot.assert_match(executed)

    assign_perm("admin", guardian_api_client.user, project)
    executed2 = guardian_api_client.execute(
        CHILD_PAST_EVENTS_QUERY, variables=variables
    )

    # having admin rights on the project should not affect past events
    assert (
        executed2["data"]["child"]["pastEvents"]
        == executed["data"]["child"]["pastEvents"]
    )


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
    (
        (None, 2),  # the 3 last ones, after 2nd -- 3,4,5
        (2, None),  # only 2 from the start -- 1,2
        (2, 2),  # only 2 after 2nd -- 3,4
        (10, None),  # all from start -- 1,2,3,4,5
        (None, 5),
    ),  # none, because offset in the last one
)
def test_children_offset_pagination(
    snapshot, project_user_api_client, project, limit, offset
):
    for i in range(1, 6):
        ChildWithGuardianFactory(name=i, project=project)
    variables = {"projectId": get_global_id(project), "limit": limit, "offset": offset}

    executed = project_user_api_client.execute(
        CHILDREN_PAGINATION_QUERY,
        variables=variables,
    )

    snapshot.assert_match(executed)


@pytest.mark.parametrize(
    "page, expected_item_count_in_page",
    (
        (1, 20),  # 1st page
        (2, 20),  # 2nd page
        (3, 20),  # 3rd page - a page that has been problematic earlier
        (4, 10),  # 4th page - a page that should be halfly filled
        (5, 0),  # 5th page - a page out of scope
    ),
)
def test_children_pagination_result_set(
    project_user_api_client, project, page, expected_item_count_in_page
):
    """
    Check that the pages has right result set when there is a greater
    amount of data.
    NOTE: There has been problems when there has been
    a greater amount of data (~70 items in KK-1049) and page size
    has been over 20. Then the pages after 2nd page all failed.
    """
    # There should be tens of items of data and the last page should not be full.
    total_count = 70
    limit = 20  # There should be more than 2 pages.
    offset = (page - 1) * limit

    with disable_auditlog():
        ChildWithGuardianFactory.create_batch(total_count, project=project)

    variables = {"projectId": get_global_id(project), "limit": limit, "offset": offset}
    executed = project_user_api_client.execute(
        CHILDREN_PAGINATION_QUERY,
        variables=variables,
    )

    assert len(executed["data"]["children"]["edges"]) == expected_item_count_in_page


@pytest.mark.parametrize("page", list(range(1, 5)))
@pytest.mark.parametrize("limit", [2, 10, 20, 25])
def test_children_pagination_cursor_works_the_same_with_offset_and_after(
    project_user_api_client, project, page, limit
):
    """
    Check that the query returns same results no matter which one
    is used with the pagination,the combination of a limit and an offset
    or a first and an after.
    NOTE: There has been problems when there has been a greater amount of data
    (~70 items in KK-1049) and page size has been over 20.
    Then the pages after 2nd page all failed.
    """
    query = """
    query Children($projectId: ID!, $limit: Int, $offset: Int, $after: String, $first: Int) {
        children(projectId: $projectId, limit: $limit, offset: $offset, after: $after, first: $first) {
            count
            edges {
            cursor
            node {
                name
            }
            }
        }
    }
    """  # noqa: E501,

    with disable_auditlog():
        ChildWithGuardianFactory.create_batch(110, project=project)

        offset = (page - 1) * limit
        executed_with_offset = project_user_api_client.execute(
            query,
            variables={
                "projectId": get_global_id(project),
                "limit": limit,
                "offset": offset,
            },
        )

        # NOTE: There will be 1 result less in the after-query,
        # because the after-parameter is read from the first result
        # and the cursor set in after, is not included in the result set.
        first = limit - 1
        after = executed_with_offset["data"]["children"]["edges"][0]["cursor"]
        executed_with_after = project_user_api_client.execute(
            query,
            variables={
                "projectId": get_global_id(project),
                "first": first,
                "after": after,
            },
        )

    assert len(executed_with_after["data"]["children"]["edges"]) == first
    assert (
        executed_with_after["data"]["children"]["edges"]
        == executed_with_offset["data"]["children"]["edges"][1:]
    )


@pytest.mark.parametrize("page", list(range(1, 5)))
@pytest.mark.parametrize("limit", [1, 2, 10, 20])
def test_children_pagination_cursor_generation(
    project_user_api_client, project, page, limit
):
    """
    Test that the cursors are created as expected.
    NOTE: There has been problems when there has been a greater amount of data
    (~70 items in KK-1049) and page size has been over 20.
    Then the pages after 2nd page all failed.
    """
    total_count = 100
    offset = (page - 1) * limit

    with disable_auditlog():
        ChildWithGuardianFactory.create_batch(total_count, project=project)

        query = """
        query Children($projectId: ID!, $limit: Int, $offset: Int) {
            children(projectId: $projectId, limit: $limit, offset: $offset) {
                edges {
                    cursor
                }
            }
        }
        """  # noqa: E501

        executed_with_offset = project_user_api_client.execute(
            query,
            variables={
                "projectId": get_global_id(project),
                "limit": limit,
                "offset": offset,
            },
        )

        cursors = [
            edge["cursor"] for edge in executed_with_offset["data"]["children"]["edges"]
        ]
    assert len(cursors) == limit

    expected_cursors = [
        offset_to_cursor(offset + index) for index, _ in enumerate(cursors)
    ]
    assert cursors == expected_cursors


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


def test_children_query_ordering(
    snapshot, project, project_user_with_global_view_families_perm_api_client
):
    with freeze_time("2020-12-12"):
        ChildWithGuardianFactory(name="Alpha", project=project)
        ChildWithGuardianFactory(name="Bravo", project=project)
        ChildWithGuardianFactory(name="Bravo", project=project)
        ChildWithGuardianFactory(name="Delta", project=project)
        ChildWithGuardianFactory(name="Charlie", project=project)
        ChildWithGuardianFactory(name="", project=project)
    with freeze_time("2020-11-11"):
        ChildWithGuardianFactory(name="", project=project)
        ChildWithGuardianFactory(name="Charlie", project=project)

    executed = project_user_with_global_view_families_perm_api_client.execute(
        """
    query Children {
      children {
        edges {
          node {
            createdAt
            name
          }
        }
      }
    }
    """
    )

    snapshot.assert_match(executed)


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
        occurrence=OccurrenceFactory(
            time=future, event=EventFactory(published_at=now())
        ),
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


def test_upcoming_events_and_event_groups(
    snapshot,
    guardian_api_client,
    child_with_user_guardian,
    future,
    past,
    project,
    another_project,
):
    # Don't check for enrolment limit in this test
    project.enrolment_limit = 10
    project.save()

    # the following should NOT be returned
    EventFactory(name="Event without occurrences", published_at=now())
    OccurrenceFactory(event__name="Unpublished event", time=future)
    OccurrenceFactory(event__published_at=now(), event__name="Event in past", time=past)
    OccurrenceFactory(
        time=future,
        event__name="Event from another project",
        event__published_at=now(),
        event__project=another_project,
    )
    EventGroupFactory(name="Empty event group", published_at=now())
    OccurrenceFactory(
        time=future,
        event__event_group=EventGroupFactory(name="Unpublished event group"),
    )
    EventFactory(
        event_group=EventGroupFactory(
            name="Event group without occurrences", published_at=now()
        ),
        published_at=now(),
    )

    OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__project=another_project,
        event__event_group=EventGroupFactory(
            published_at=now(), project=another_project
        ),
    )  # event group from another project

    # the following should be returned (canChildEnroll == False)
    EnrolmentFactory(
        child=child_with_user_guardian,
        occurrence=OccurrenceFactory(
            time=future,
            event=EventFactory(
                name="This should be 7/8", published_at=now() - timedelta(minutes=70)
            ),
        ),
    )
    event_group = EventGroupFactory(
        name="This should be 8/8", published_at=now() - timedelta(minutes=80)
    )
    event_group_occurrences = OccurrenceFactory.create_batch(
        2,
        time=timezone.now(),
        event__published_at=now(),
        event__event_group=event_group,
    )
    EnrolmentFactory(
        child=child_with_user_guardian, occurrence=event_group_occurrences[0]
    )
    OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__event_group=EventGroupFactory(
            name="This should be 6/8", published_at=now() + timedelta(minutes=10)
        ),
    )
    OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__event_group=EventGroupFactory(
            name="This should be the 1/8", published_at=now() + timedelta(minutes=60)
        ),
    )
    OccurrenceFactory(
        time=future,
        event=EventFactory(
            published_at=now() + timedelta(minutes=50), name="This should be 2/8"
        ),
    )
    OccurrenceFactory(
        time=future,
        event=EventFactory(
            published_at=now() + timedelta(minutes=20), name="This should be 5/8"
        ),
    )

    # Ticketmaster events
    RandomExternalTicketSystemEventFactory(
        ticket_system=Event.TICKETMASTER,
        published_at=now() + timedelta(minutes=40),
        name="This should be 3/8",
    )
    RandomExternalTicketSystemEventFactory(
        ticket_system=Event.LIPPUPISTE,
        published_at=now() + timedelta(minutes=30),
        name="This should be 4/8",
        ticket_system_end_time=now() + timedelta(minutes=60),
    )
    RandomExternalTicketSystemEventFactory(
        published_at=now() + timedelta(minutes=10),
        name="ERROR: Event in the past",
        ticket_system_end_time=now() - timedelta(minutes=1),
    )
    RandomExternalTicketSystemEventFactory(
        published_at=now() + timedelta(minutes=10),
        name="ERROR: Event from another project",
        ticket_system_end_time=now() + timedelta(minutes=1),
        project=ProjectFactory(year=3000),
    )

    variables = {"id": get_global_id(child_with_user_guardian)}
    executed = guardian_api_client.execute(
        CHILD_UPCOMING_EVENTS_AND_EVENT_GROUPS_QUERY, variables=variables
    )

    snapshot.assert_match(executed)

    assign_perm("admin", guardian_api_client.user, project)
    executed2 = guardian_api_client.execute(
        CHILD_UPCOMING_EVENTS_AND_EVENT_GROUPS_QUERY, variables=variables
    )

    # having admin rights on the project should not affect available events
    assert (
        executed2["data"]["child"]["upcomingEventsAndEventGroups"]
        == executed["data"]["child"]["upcomingEventsAndEventGroups"]
    )


@pytest.mark.parametrize("enrolments_in_future", [True, False])
def test_test_upcoming_events_and_event_groups_yearly_enrolment_limit(
    snapshot,
    guardian_api_client,
    child_with_user_guardian,
    future,
    past,
    project,
    enrolments_in_future,
):
    project.enrolment_limit = 2
    project.save()

    OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__event_group=EventGroupFactory(
            name="This should be the first", published_at=now() + timedelta(minutes=2)
        ),
    )
    OccurrenceFactory(
        time=future,
        event=EventFactory(
            published_at=now() + timedelta(minutes=1), name="This should be the second"
        ),
    )

    occurrence_time = future if enrolments_in_future else past
    publish_time = min(occurrence_time, now())

    EnrolmentFactory(
        child=child_with_user_guardian,
        occurrence=OccurrenceFactory(
            time=occurrence_time,
            event=EventFactory(name="Enrolled event", published_at=publish_time),
        ),
    )
    EnrolmentFactory(
        child=child_with_user_guardian,
        occurrence=OccurrenceFactory(
            time=occurrence_time,
            event=EventFactory(
                name="Enrolled event",
                published_at=publish_time,
                event_group=EventGroupFactory(
                    name="Enrolled event group", published_at=publish_time
                ),
            ),
        ),
    )

    variables = {"id": get_global_id(child_with_user_guardian)}
    executed = guardian_api_client.execute(
        CHILD_UPCOMING_EVENTS_AND_EVENT_GROUPS_QUERY, variables=variables
    )

    nodes = executed["data"]["child"]["upcomingEventsAndEventGroups"]["edges"]

    if enrolments_in_future:
        assert len(nodes) == 4
    else:
        assert len(nodes) == 2

    for node in nodes:
        assert node["node"]["canChildEnroll"] is False


def test_active_internal_and_ticketmaster_enrolments(
    snapshot,
    guardian_api_client,
    child_with_user_guardian,
    future,
    past,
):
    # unenrolled event, should not be returned
    OccurrenceFactory(
        event__name="INCORRECT 1",
        event__published_at=now(),
        time=future,
    )

    # unassigned Ticketmaster password, should not be returned
    password_0 = TicketSystemPasswordFactory(
        event=EventFactory(
            published_at=now(),
            ticket_system=Event.TICKETMASTER,
            name="INCORRECT 2",
        ),
    )
    OccurrenceFactory(event=password_0.event, time=future)

    # enrolment in the past, should not be returned
    enrolment = EnrolmentFactory(
        child=child_with_user_guardian,
        occurrence=OccurrenceFactory(
            time=past,
            event=EventFactory(published_at=now(), name="INCORRECT 3"),
        ),
    )
    # add also one occurrence in the future, should not affect anything
    OccurrenceFactory(event=enrolment.occurrence.event, time=future)

    # enrolment in the future + 1 day, should be returned as the second enrolment
    enrolment = EnrolmentFactory(
        child=child_with_user_guardian,
        occurrence=OccurrenceFactory(
            time=future + timedelta(days=1),
            event=EventFactory(published_at=now(), name="2/5"),
        ),
    )
    # add also one occurrence in the past, should not affect anything
    OccurrenceFactory(event=enrolment.occurrence.event, time=past)

    # enrolment in the future + 3 days, should be returned as the fourth enrolment
    enrolment = EnrolmentFactory(
        child=child_with_user_guardian,
        occurrence=OccurrenceFactory(
            time=future + timedelta(days=3),
            event=EventFactory(published_at=now(), name="4/5"),
        ),
    )

    # Ticketmaster password whose event ends in the past, should not be returned
    TicketSystemPasswordFactory(
        event=EventFactory(
            published_at=now(),
            ticket_system=Event.TICKETMASTER,
            name="INCORRECT 4",
            ticket_system_end_time=past,
        ),
        child=child_with_user_guardian,
        assigned_at=now(),
    )

    # Ticketmaster password whose event ends right now, should be returned as the
    # first enrolment
    TicketSystemPasswordFactory(
        event=EventFactory(
            published_at=now(),
            ticket_system=Event.TICKETMASTER,
            name="1/5",
            ticket_system_end_time=now(),
        ),
        child=child_with_user_guardian,
        assigned_at=now(),
    )

    # Ticketmaster password whose event does not have an end time, should be returned
    # as the last enrolment
    TicketSystemPasswordFactory(
        event=EventFactory(
            published_at=now(), ticket_system=Event.TICKETMASTER, name="5/5"
        ),
        child=child_with_user_guardian,
        assigned_at=now(),
    )

    # Ticketmaster password whose event's ends at "future" + 2 days, should be returned
    # as the third enrolment
    TicketSystemPasswordFactory(
        event=EventFactory(
            published_at=now(),
            ticket_system=Event.TICKETMASTER,
            name="3/5",
            ticket_system_end_time=future + timedelta(days=2),
        ),
        child=child_with_user_guardian,
        assigned_at=now(),
    )

    variables = {"id": get_global_id(child_with_user_guardian)}
    executed = guardian_api_client.execute(
        CHILD_ACTIVE_INTERNAL_AND_TICKETMASTER_ENROLMENTS_QUERY, variables=variables
    )

    snapshot.assert_match(executed)
