from copy import deepcopy

import pytest
from guardian.shortcuts import assign_perm

from children.factories import RelationshipFactory
from children.tests.test_api import (
    assert_guardian_matches_data,
    assert_permission_denied,
)
from common.tests.conftest import create_api_client_with_user
from common.tests.utils import assert_match_error_code
from common.utils import get_global_id
from kukkuu.consts import INVALID_EMAIL_FORMAT_ERROR
from projects.factories import ProjectFactory
from users.factories import GuardianFactory
from users.models import Guardian


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


GUARDIANS_QUERY = """
query Guardians {
  guardians {
    edges {
      node {
        firstName
        lastName
        phoneNumber
        email
        relationships {
          edges {
            node {
              type
              child {
                firstName
                birthdate
                project {
                  year
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


def test_guardians_query_unauthenticated(api_client):
    executed = api_client.execute(GUARDIANS_QUERY)

    assert_permission_denied(executed)


def test_guardians_query_normal_user(snapshot, user_api_client, project):
    GuardianFactory(relationships__count=1, relationships__child__project=project)
    GuardianFactory(
        user=user_api_client.user,
        relationships__count=1,
        relationships__child__project=project,
    )

    executed = user_api_client.execute(GUARDIANS_QUERY)

    snapshot.assert_match(executed)


def test_guardians_query_project_user(
    snapshot, project_user_api_client, project, another_project
):
    guardian_1 = GuardianFactory(
        first_name="Guardian having children in own and another project",
        last_name="Should be visible 1/2",
        relationships__count=1,
        relationships__child__project=project,
    )
    RelationshipFactory(
        guardian=guardian_1,
        child__first_name="Second child from another project - Should NOT be visible",
        child__project=another_project,
    )

    GuardianFactory(
        first_name="Another project own guardian",
        last_name="Should be visible 2/2",
        user=project_user_api_client.user,
        relationships__count=1,
        relationships__child__project=another_project,
    )

    GuardianFactory(
        first_name="Another project guardian",
        last_name="Should NOT be visible",
        relationships__count=1,
        relationships__child__project=another_project,
    )

    executed = project_user_api_client.execute(GUARDIANS_QUERY)

    snapshot.assert_match(executed)


MY_PROFILE_QUERY = """
query MyProfile {
  myProfile {
    firstName
    lastName
    phoneNumber
    email
    relationships {
      edges {
        node {
          type
          child {
            firstName
            birthdate
            postalCode
          }
        }
      }
    }
    language
    languagesSpokenAtHome {
      edges {
        node {
          alpha3Code
        }
      }
    }
  }
}
"""

MY_ADMIN_PROFILE_QUERY = """
query MyAdminProfle{
  myAdminProfile{
    projects {
      edges {
        node {
          name
          myPermissions {
            publish
            manageEventGroups
          }
        }
      }
    }
  }
}
"""


def test_my_profile_query_unauthenticated(api_client):
    GuardianFactory()

    executed = api_client.execute(MY_PROFILE_QUERY)

    assert executed["data"]["myProfile"] is None
    assert_permission_denied(executed)


def test_my_profile_query(snapshot, user_api_client, project):
    GuardianFactory()
    GuardianFactory(
        user=user_api_client.user,
        relationships__count=1,
        relationships__child__project=project,
    )
    GuardianFactory(relationships__count=1, relationships__child__project=project)

    executed = user_api_client.execute(MY_PROFILE_QUERY)

    snapshot.assert_match(executed)


@pytest.mark.parametrize("guardian_email", ["guardian@example.com", ""])
def test_my_profile_query_email(snapshot, guardian_email):
    guardian = GuardianFactory(email=guardian_email, user__email="user@example.com")
    api_client = create_api_client_with_user(guardian.user)

    executed = api_client.execute(
        """
query MyProfile {
  myProfile {
    email
  }
}
"""
    )

    snapshot.assert_match(executed)


def test_my_profile_no_profile(snapshot, user_api_client):
    GuardianFactory()

    executed = user_api_client.execute(MY_PROFILE_QUERY)

    snapshot.assert_match(executed)


UPDATE_MY_PROFILE_MUTATION = """
mutation UpdateMyProfile($input: UpdateMyProfileMutationInput!) {
  updateMyProfile(input: $input) {
    myProfile {
      firstName
      lastName
      phoneNumber
      language
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

UPDATE_MY_PROFILE_VARIABLES = {
    "input": {
        "firstName": "Updated First Name",
        "lastName": "Updated Last Name",
        "phoneNumber": "Updated phone number",
        "language": "EN",
        "languagesSpokenAtHome": [],
    }
}


def test_update_my_profile_mutation_unauthenticated(api_client):
    executed = api_client.execute(
        UPDATE_MY_PROFILE_MUTATION, variables=UPDATE_MY_PROFILE_VARIABLES
    )

    assert_permission_denied(executed)


def test_update_my_profile_mutation(snapshot, user_api_client, languages):
    GuardianFactory(user=user_api_client.user, language="fi")
    variables = deepcopy(UPDATE_MY_PROFILE_VARIABLES)
    variables["input"]["languagesSpokenAtHome"] = [
        get_global_id(language) for language in languages[0:2]
    ]  # fin, swe

    executed = user_api_client.execute(UPDATE_MY_PROFILE_MUTATION, variables=variables)

    snapshot.assert_match(executed)
    guardian = Guardian.objects.get(user=user_api_client.user)
    assert_guardian_matches_data(guardian, variables["input"])


@pytest.mark.parametrize(
    "guardian_email, is_valid",
    [
        ("guardian_updated@example.com", True),
        ("INVALID_EMAIL", False),
        ("", False),
        (None, False),
    ],
)
def test_update_my_profile_mutation_email(snapshot, guardian_email, is_valid):
    guardian = GuardianFactory(
        email="guardian_original@example.com", user__email="user@example.com"
    )
    api_client = create_api_client_with_user(guardian.user)

    executed = api_client.execute(
        """
mutation UpdateMyProfile($input: UpdateMyProfileMutationInput!) {
  updateMyProfile(input: $input) {
    myProfile {
      email
    }
  }
}
""",
        variables={"input": {"email": guardian_email}},
    )

    guardian.refresh_from_db()
    if is_valid:
        snapshot.assert_match(executed)
        assert guardian.email == guardian_email
    else:
        assert_match_error_code(executed, INVALID_EMAIL_FORMAT_ERROR)
        assert guardian.email == "guardian_original@example.com"


def test_my_admin_profile_unauthenticated(api_client):
    executed = api_client.execute(MY_ADMIN_PROFILE_QUERY)
    assert_permission_denied(executed)


def test_my_admin_profile_normal_user(user_api_client):
    ProjectFactory(year=2021, name="some project")
    executed = user_api_client.execute(MY_ADMIN_PROFILE_QUERY)
    assert executed["data"]["myAdminProfile"]["projects"]["edges"] == []


@pytest.mark.parametrize(
    "has_also_model_perms", (False, True), ids=("no_model_perm", "has_also_model_perm")
)
def test_my_admin_profile_project_admin(
    snapshot, user_api_client, has_also_model_perms
):
    project_1 = ProjectFactory(
        year=2021, name="project where base admin object perm but no other object perms"
    )
    project_2 = ProjectFactory(
        year=2022, name="project where base admin object perm and other object perms"
    )
    assign_perm("admin", user_api_client.user, [project_1, project_2])
    assign_perm("publish", user_api_client.user, project_2)
    assign_perm("manage_event_groups", user_api_client.user, project_2)

    if has_also_model_perms:
        assign_perm("projects.admin", user_api_client.user)
        assign_perm("projects.publish", user_api_client.user)
        assign_perm("projects.manage_event_groups", user_api_client.user)

    ProjectFactory(year=2030, name="project where no object perms")

    executed = user_api_client.execute(MY_ADMIN_PROFILE_QUERY)

    snapshot.assert_match(executed)
