from copy import deepcopy

import pytest
from django.contrib.auth.models import Group
from django.utils import timezone
from guardian.shortcuts import assign_perm

from children.factories import RelationshipFactory
from children.tests.test_api import (
    assert_guardian_matches_data,
    assert_permission_denied,
)
from common.tests.conftest import create_api_client_with_user
from common.tests.utils import assert_match_error_code
from common.utils import get_global_id
from events.factories import EventFactory
from kukkuu.consts import INVALID_EMAIL_FORMAT_ERROR, VERIFICATION_TOKEN_INVALID_ERROR
from organisations.factories import OrganisationFactory
from projects.factories import ProjectFactory
from projects.models import ProjectPermission
from users.factories import GuardianFactory
from users.models import Guardian
from users.tests.mutations import (
    REQUEST_EMAIL_CHANGE_TOKEN_MUTATION,
    UPDATE_MY_COMMUNICATION_SUBSCRIPTIONS_MUTATION,
    UPDATE_MY_EMAIL_MUTATION,
    UPDATE_MY_PROFILE_MUTATION,
)
from users.tests.queries import (
    GUARDIANS_QUERY,
    MY_ADMIN_PROFILE_QUERY,
    MY_COMMUNICATION_SUBSCRIPTIONS_QUERY,
    MY_PROFILE_QUERY,
)
from verification_tokens.factories import (
    UserEmailVerificationTokenFactory,
    UserSubscriptionsAuthVerificationTokenFactory,
)


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


def test_guardians_query_unauthenticated(api_client):
    executed = api_client.execute(GUARDIANS_QUERY)

    assert_permission_denied(executed)


def test_guardians_query_normal_user(user_api_client):
    executed = user_api_client.execute(GUARDIANS_QUERY)

    assert_permission_denied(executed)


def test_guardians_query_project_user(project_user_api_client):
    """
    Test that project user with a project specific permission, but no global
    permission, to view families will get permission denied, if trying to
    query all guardians in all projects.
    """
    executed = project_user_api_client.execute(GUARDIANS_QUERY)
    assert_permission_denied(executed)


def test_guardians_query_project_user_with_global_view_families_perm(
    snapshot, project_user_api_client, project, another_project
):
    """
    Test that project user with a global permission to view families, and
    admin permission to a project, will get all guardians from the project
    they have admin permission to, but not from other projects.
    """
    guardian_1 = GuardianFactory(
        first_name="Guardian having children in own and another project",
        last_name="Should be visible 1/2",
        relationships__count=1,
        relationships__child__project=project,
    )
    RelationshipFactory(
        guardian=guardian_1,
        child__name="Second child from another project - Should NOT be visible",
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

    # Give user global permission to view families
    assign_perm(
        ProjectPermission.VIEW_FAMILIES.permission_name, project_user_api_client.user
    )

    executed = project_user_api_client.execute(GUARDIANS_QUERY)

    snapshot.assert_match(executed)


def test_guardians_query_project_user_no_view_families_perm(
    project_user_no_view_families_perm_api_client,
):
    executed = project_user_no_view_families_perm_api_client.execute(GUARDIANS_QUERY)
    assert_permission_denied(executed)


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


@pytest.mark.parametrize("has_accepted_communication", [True, False])
def test_my_communication_subscriptions_query_as_logged_in(
    has_accepted_communication, snapshot, guardian_api_client
):
    guardian = guardian_api_client.user.guardian
    guardian.has_accepted_communication = has_accepted_communication
    guardian.save()
    executed = guardian_api_client.execute(MY_COMMUNICATION_SUBSCRIPTIONS_QUERY)
    assert (
        executed["data"]["myCommunicationSubscriptions"]["firstName"]
        == guardian.first_name
    )
    assert (
        executed["data"]["myCommunicationSubscriptions"]["hasAcceptedCommunication"]
        == guardian.has_accepted_communication
    )
    snapshot.assert_match(executed)


def test_my_communication_subscriptions_query_with_auth_verification_token(
    snapshot, api_client
):
    guardian = GuardianFactory(has_accepted_communication=True)
    auth_verification_token = UserSubscriptionsAuthVerificationTokenFactory(
        user=guardian.user
    )
    executed = api_client.execute(
        MY_COMMUNICATION_SUBSCRIPTIONS_QUERY,
        variables={"authToken": auth_verification_token.key},
    )
    assert (
        executed["data"]["myCommunicationSubscriptions"]["firstName"]
        == guardian.first_name
    )
    assert (
        executed["data"]["myCommunicationSubscriptions"]["hasAcceptedCommunication"]
        == guardian.has_accepted_communication
    )
    snapshot.assert_match(executed)


def test_my_communication_subscriptions_query_unauthenticated(api_client):
    # no matter if a token exists
    UserSubscriptionsAuthVerificationTokenFactory()
    # no auth token given nor authorization header given
    executed = api_client.execute(
        MY_COMMUNICATION_SUBSCRIPTIONS_QUERY,
        variables={},
    )
    assert_permission_denied(executed)


def test_my_communication_subscriptions_query_with_invalid_auth_verification_token(
    api_client,
):
    # no matter if a token exists
    UserSubscriptionsAuthVerificationTokenFactory()
    # no auth token given nor authorization header given
    executed = api_client.execute(
        MY_COMMUNICATION_SUBSCRIPTIONS_QUERY,
        variables={"authToken": "invalid token"},
    )
    assert_permission_denied(executed)


UPDATE_MY_PROFILE_VARIABLES = {
    "input": {
        "firstName": "Updated First Name",
        "lastName": "Updated Last Name",
        "phoneNumber": "Updated phone number",
        "language": "EN",
        "languagesSpokenAtHome": [],
        "hasAcceptedCommunication": False,
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
    "new_email, is_valid",
    [
        ("changed-email@kummilapset.fi", True),
        ("INVALID_EMAIL", False),
        ("", False),
        (None, False),
    ],
)
def test_update_my_email_mutation(snapshot, user_api_client, new_email, is_valid):
    initial_email = "initial-email@kummilapset.fi"
    user = user_api_client.user
    GuardianFactory(user=user, email=initial_email)
    verification_token = UserEmailVerificationTokenFactory(user=user, email=new_email)
    variables = {
        "input": {"email": new_email, "verificationToken": verification_token.key}
    }
    executed = user_api_client.execute(UPDATE_MY_EMAIL_MUTATION, variables=variables)
    guardian = Guardian.objects.get(user=user)
    if is_valid:
        snapshot.assert_match(executed)
        assert guardian.email == new_email
    elif new_email is None:
        assert len(executed["errors"]) == 1
        assert "Variable '$input' got invalid value" in executed["errors"][0]["message"]
    else:
        assert_match_error_code(executed, INVALID_EMAIL_FORMAT_ERROR)
        assert guardian.email == initial_email


def test_update_my_email_mutation_with_invalid_token(user_api_client):
    user = user_api_client.user
    initial_email = "initial-email@kummilapset.fi"
    new_email = "changed-email@kummilapset.fi"
    GuardianFactory(user=user, email=initial_email)
    UserEmailVerificationTokenFactory(user=user, email=new_email)
    variables = {
        "input": {
            "email": new_email,
            "verificationToken": "invalid-key",
        }
    }
    executed = user_api_client.execute(UPDATE_MY_EMAIL_MUTATION, variables=variables)
    assert_match_error_code(executed, VERIFICATION_TOKEN_INVALID_ERROR)
    guardian = Guardian.objects.get(user=user)
    assert guardian.email == initial_email


def test_update_my_email_mutation_with_expired_token(user_api_client, settings):
    settings.VERIFICATION_TOKEN_VALID_MINUTES = 10
    user = user_api_client.user
    initial_email = "initial-email@kummilapset.fi"
    GuardianFactory(user=user, email=initial_email)
    date_expired = timezone.now() - timezone.timedelta(
        minutes=(settings.VERIFICATION_TOKEN_VALID_MINUTES + 1)
    )
    assert date_expired < timezone.now()
    verification_token = UserEmailVerificationTokenFactory(
        user=user,
        expiry_date=date_expired,
    )
    variables = {
        "input": {
            "email": "changed-email@kummilapset.fi",
            "verificationToken": verification_token.key,
        }
    }
    executed = user_api_client.execute(UPDATE_MY_EMAIL_MUTATION, variables=variables)
    assert_match_error_code(executed, VERIFICATION_TOKEN_INVALID_ERROR)
    guardian = Guardian.objects.get(user=user)
    assert guardian.email == initial_email


def test_update_my_email_mutation_with_wrong_email(user_api_client):
    user = user_api_client.user
    initial_email = "initial-email@kummilapset.fi"
    new_email = "changed-email@kummilapset.fi"
    GuardianFactory(user=user, email=initial_email)

    verification_token_with_old_email = UserEmailVerificationTokenFactory(
        user=user, email=user.guardian.email
    )
    variables = {
        "input": {
            "email": new_email,
            "verificationToken": verification_token_with_old_email.key,
        }
    }
    executed = user_api_client.execute(UPDATE_MY_EMAIL_MUTATION, variables=variables)
    assert_match_error_code(executed, VERIFICATION_TOKEN_INVALID_ERROR)

    verification_token_with_old_email = UserEmailVerificationTokenFactory(user=user)
    variables = {
        "input": {
            "email": new_email,
            "verificationToken": verification_token_with_old_email.key,
        }
    }
    executed = user_api_client.execute(UPDATE_MY_EMAIL_MUTATION, variables=variables)
    assert_match_error_code(executed, VERIFICATION_TOKEN_INVALID_ERROR)

    guardian = Guardian.objects.get(user=user)
    assert guardian.email == initial_email


def test_update_my_email_mutation_unauthenticated(api_client):
    variables = {
        "input": {
            "email": "changed-email@kummilapset.fi",
            "verificationToken": "something",
        }
    }
    executed = api_client.execute(UPDATE_MY_EMAIL_MUTATION, variables=variables)
    assert_permission_denied(executed)


def test_request_email_change_token_mutation(snapshot, user_api_client):
    GuardianFactory(user=user_api_client.user)
    variables = {"input": {"email": "new-email@kummilapset.fi"}}
    executed = user_api_client.execute(
        REQUEST_EMAIL_CHANGE_TOKEN_MUTATION, variables=variables
    )
    snapshot.assert_match(executed)


def test_request_email_change_token_mutation_without_guardian(user_api_client):
    variables = {"input": {"email": "new-email@kummilapset.fi"}}
    executed = user_api_client.execute(
        REQUEST_EMAIL_CHANGE_TOKEN_MUTATION, variables=variables
    )
    assert len(executed["errors"]) == 1
    assert "User has no guardian." in executed["errors"][0]["message"]


def test_request_email_change_token_mutation_unauthenticated(api_client):
    variables = {"input": {"email": "new-email@kummilapset.fi"}}
    executed = api_client.execute(
        REQUEST_EMAIL_CHANGE_TOKEN_MUTATION, variables=variables
    )
    assert_permission_denied(executed)


def test_my_admin_profile_unauthenticated(api_client):
    executed = api_client.execute(MY_ADMIN_PROFILE_QUERY)
    assert_permission_denied(executed)


def test_my_admin_profile_normal_user(user_api_client):
    ProjectFactory(year=2031, name="some project")
    executed = user_api_client.execute(MY_ADMIN_PROFILE_QUERY)
    assert executed["data"]["myAdminProfile"]["projects"]["edges"] == []


MY_ADMIN_PROFILE_ROLES_QUERY = """
query MyAdminProfileRoles {
  myAdminProfile {
    isEventOrganiser
    isSystemAdministrator
    organisations {
      edges {
        node {
          name
        }
      }
    }
  }
}
"""


def test_my_admin_profile_roles_normal_user(user_api_client):
    executed = user_api_client.execute(MY_ADMIN_PROFILE_ROLES_QUERY)
    assert executed["data"]["myAdminProfile"] == {
        "isEventOrganiser": False,
        "isSystemAdministrator": False,
        "organisations": {"edges": []},
    }


def test_my_admin_profile_roles_project_admin_without_organisation(user_api_client):
    project = ProjectFactory(year=2031)
    assign_perm(ProjectPermission.ADMIN.value, user_api_client.user, project)
    executed = user_api_client.execute(MY_ADMIN_PROFILE_ROLES_QUERY)
    assert executed["data"]["myAdminProfile"] == {
        "isEventOrganiser": False,
        "isSystemAdministrator": False,
        "organisations": {"edges": []},
    }


def test_my_admin_profile_roles_project_admin_with_organisation(user_api_client):
    project = ProjectFactory(year=2031)
    assign_perm(ProjectPermission.ADMIN.value, user_api_client.user, project)
    org = OrganisationFactory()
    user_api_client.user.organisations.add(org)
    executed = user_api_client.execute(MY_ADMIN_PROFILE_ROLES_QUERY)
    assert executed["data"]["myAdminProfile"]["isEventOrganiser"] is True
    assert executed["data"]["myAdminProfile"]["isSystemAdministrator"] is False
    assert len(executed["data"]["myAdminProfile"]["organisations"]["edges"]) == 1
    assert (
        executed["data"]["myAdminProfile"]["organisations"]["edges"][0]["node"]["name"]
        == org.name
    )


def test_my_admin_profile_roles_system_administrator(user_api_client):
    user_api_client.user.is_staff = True
    user_api_client.user.save()
    executed = user_api_client.execute(MY_ADMIN_PROFILE_ROLES_QUERY)
    assert executed["data"]["myAdminProfile"]["isEventOrganiser"] is True
    assert executed["data"]["myAdminProfile"]["isSystemAdministrator"] is True


def test_my_admin_profile_roles_system_organisation_member(user_api_client):
    system_org = OrganisationFactory(is_system=True)
    user_api_client.user.organisations.add(system_org)
    executed = user_api_client.execute(MY_ADMIN_PROFILE_ROLES_QUERY)
    assert executed["data"]["myAdminProfile"]["isEventOrganiser"] is False
    assert executed["data"]["myAdminProfile"]["isSystemAdministrator"] is False


@pytest.mark.parametrize(
    "has_also_model_perms", (False, True), ids=("no_model_perm", "has_also_model_perm")
)
def test_my_admin_profile_project_admin(
    snapshot, user_api_client, has_also_model_perms
):
    project_1 = ProjectFactory(
        year=2031, name="project where base admin object perm but no other object perms"
    )
    project_2 = ProjectFactory(
        year=2032, name="project where base admin object perm and other object perms"
    )
    assign_perm(
        ProjectPermission.ADMIN.value, user_api_client.user, [project_1, project_2]
    )
    assign_perm(ProjectPermission.PUBLISH.value, user_api_client.user, project_2)
    assign_perm(
        ProjectPermission.MANAGE_EVENT_GROUPS.value, user_api_client.user, project_2
    )
    assign_perm(
        ProjectPermission.SEND_MESSAGE_TO_ALL_IN_PROJECT.value,
        user_api_client.user,
        project_2,
    )

    if has_also_model_perms:
        assign_perm(ProjectPermission.ADMIN.permission_name, user_api_client.user)
        assign_perm(ProjectPermission.PUBLISH.permission_name, user_api_client.user)
        assign_perm(
            ProjectPermission.MANAGE_EVENT_GROUPS.permission_name, user_api_client.user
        )
        assign_perm(
            ProjectPermission.SEND_MESSAGE_TO_ALL_IN_PROJECT.permission_name,
            user_api_client.user,
        )

    ProjectFactory(year=2030, name="project where no object perms")

    executed = user_api_client.execute(MY_ADMIN_PROFILE_QUERY)

    snapshot.assert_match(executed)


@pytest.mark.parametrize("initial_has_accepted_communication", [False, True])
def test_update_my_communication_subscriptions_as_logged_in(
    initial_has_accepted_communication, snapshot, user_api_client
):
    user = user_api_client.user
    guardian = GuardianFactory(
        user=user, has_accepted_communication=initial_has_accepted_communication
    )
    executed = user_api_client.execute(
        UPDATE_MY_COMMUNICATION_SUBSCRIPTIONS_MUTATION,
        variables={
            "input": {
                "hasAcceptedCommunication": not initial_has_accepted_communication
            }
        },
    )
    assert (
        executed["data"]["updateMyCommunicationSubscriptions"]["guardian"]["firstName"]
        == guardian.first_name
    )
    assert (
        executed["data"]["updateMyCommunicationSubscriptions"]["guardian"][
            "hasAcceptedCommunication"
        ]
        is not initial_has_accepted_communication
    )
    assert guardian.has_accepted_communication is not initial_has_accepted_communication
    snapshot.assert_match(executed)


@pytest.mark.parametrize("initial_has_accepted_communication", [False, True])
def test_update_my_communication_subscriptions_with_auth_verification_token(
    initial_has_accepted_communication, snapshot, api_client
):
    guardian = GuardianFactory(
        has_accepted_communication=initial_has_accepted_communication
    )
    user = guardian.user
    auth_verification_token = UserSubscriptionsAuthVerificationTokenFactory(user=user)
    executed = api_client.execute(
        UPDATE_MY_COMMUNICATION_SUBSCRIPTIONS_MUTATION,
        variables={
            "input": {
                "hasAcceptedCommunication": not initial_has_accepted_communication,
                "authToken": auth_verification_token.key,
            }
        },
    )
    assert (
        executed["data"]["updateMyCommunicationSubscriptions"]["guardian"]["firstName"]
        == guardian.first_name
    )
    assert (
        executed["data"]["updateMyCommunicationSubscriptions"]["guardian"][
            "hasAcceptedCommunication"
        ]
        is not initial_has_accepted_communication
    )
    guardian.refresh_from_db()
    assert guardian.has_accepted_communication is not initial_has_accepted_communication
    snapshot.assert_match(executed)


@pytest.mark.parametrize(
    "variables",
    [
        {
            "input": {
                "hasAcceptedCommunication": True,
            }
        },
        {
            "input": {
                "hasAcceptedCommunication": True,
                "authToken": "invalid token",
            }
        },
    ],
)
def test_update_my_communication_subscriptions_as_unauthenticated(
    variables,
    api_client,
):
    # no matter if a token exists
    UserSubscriptionsAuthVerificationTokenFactory()
    executed = api_client.execute(
        UPDATE_MY_COMMUNICATION_SUBSCRIPTIONS_MUTATION,
        variables=variables,
    )
    assert_permission_denied(executed)


@pytest.mark.parametrize(
    "variables",
    [
        {"input": {}},
        {},
        {
            "input": {
                "authToken": "what ever",
            }
        },
    ],
)
def test_update_my_communication_subscriptions_returns_errors_without_required_args(
    variables,
    snapshot,
    guardian_api_client,
):
    executed = guardian_api_client.execute(
        UPDATE_MY_COMMUNICATION_SUBSCRIPTIONS_MUTATION,
        variables=variables,
    )
    assert_match_error_code(executed, "GENERAL_ERROR")
    snapshot.assert_match(executed)


MY_ADMIN_PROFILE_FULL_QUERY = """
query MyAdminProfileFull {
  myAdminProfile {
    isEventOrganiser
    isSystemAdministrator
    organisations {
      edges {
        node {
          name
        }
      }
    }
    projects {
      edges {
        node {
          id
          name
          year
        }
      }
    }
  }
}
"""

EVENTS_WITH_ADMIN_QUERY = """
query EventsWithAdmin($projectId: ID) {
  events(projectId: $projectId) {
    edges {
      node {
        name
        canUserAdminister
      }
    }
  }
}
"""

ORGANISATIONS_ROOT_QUERY = """
query OrganisationsRoot {
  organisations {
    edges {
      node {
        name
      }
    }
  }
}
"""


@pytest.mark.parametrize(
    (
        "is_staff",
        "org_kind",
        "has_group_perm",
        "has_global_perm",
        "expected_is_sysadmin",
        "expected_is_organiser",
        "expected_has_projects",
        "expected_has_orgs",
    ),
    [
        # Case 1: No staff, no organisation, some groups (project admin)
        (False, "none", True, False, False, False, True, False),
        # Case 2: Staff, some organisations, no groups
        (True, "regular", False, False, True, True, False, True),
        # Case 3: No staff, system organisation only, some groups (project admin)
        (False, "system", True, False, False, True, True, True),
        # Case 4: No staff, some organisations, some groups (project admin)
        (False, "multiple", True, False, False, True, True, True),
        # Case 5: Staff, any organisation, some groups (project admin)
        (True, "regular", True, False, True, True, True, True),
        # Case 6: Staff, global base admin permission, any/no organisations, any/no groups
        (True, "none", False, True, True, True, True, False),
    ],
    ids=[
        "case_1_no_staff_no_org_some_groups",
        "case_2_staff_some_orgs_no_groups",
        "case_3_no_staff_system_org_some_groups",
        "case_4_no_staff_some_orgs_some_groups",
        "case_5_staff_any_org_some_groups",
        "case_6_staff_global_perm_no_orgs_no_groups",
    ],
)
def test_my_admin_profile_use_cases(
    user_api_client,
    is_staff,
    org_kind,
    has_group_perm,
    has_global_perm,
    expected_is_sysadmin,
    expected_is_organiser,
    expected_has_projects,
    expected_has_orgs,
):
    user = user_api_client.user
    user.is_staff = is_staff

    project = ProjectFactory(year=2031, name="Project 2031")
    other_project = ProjectFactory(year=2032, name="Project 2032")

    if has_group_perm:
        group = Group.objects.create(name=f"Project 2031 Admins for {user.username}")
        assign_perm(ProjectPermission.ADMIN.value, group, project)
        user.groups.add(group)

    if has_global_perm:
        assign_perm(ProjectPermission.ADMIN.permission_name, user)

    if org_kind == "regular":
        org = OrganisationFactory(name="Regular Org")
        user.organisations.add(org)
    elif org_kind == "system":
        system_org = OrganisationFactory(name="City of Helsinki", is_system=True)
        user.organisations.add(system_org)
    elif org_kind == "multiple":
        org1 = OrganisationFactory(name="Org A")
        org2 = OrganisationFactory(name="Org B")
        user.organisations.add(org1, org2)

    user.save()
    user.__dict__.pop("administered_projects", None)

    executed = user_api_client.execute(MY_ADMIN_PROFILE_FULL_QUERY)
    profile = executed["data"]["myAdminProfile"]

    assert profile["isSystemAdministrator"] is expected_is_sysadmin
    assert profile["isEventOrganiser"] is expected_is_organiser

    returned_projects = [edge["node"]["name"] for edge in profile["projects"]["edges"]]
    if expected_has_projects:
        if has_global_perm:
            assert project.name in returned_projects
            assert other_project.name in returned_projects
        else:
            assert returned_projects == [project.name]
    else:
        assert returned_projects == []

    returned_orgs = [edge["node"]["name"] for edge in profile["organisations"]["edges"]]
    if expected_has_orgs:
        assert len(returned_orgs) > 0
    else:
        assert returned_orgs == []


def test_my_admin_profile_superuser_gets_all_projects(user_api_client):
    user = user_api_client.user
    user.is_superuser = True
    user.save()
    user.__dict__.pop("administered_projects", None)

    project1 = ProjectFactory(year=2031, name="Superuser Project 1")
    project2 = ProjectFactory(year=2032, name="Superuser Project 2")

    executed = user_api_client.execute(MY_ADMIN_PROFILE_FULL_QUERY)
    profile = executed["data"]["myAdminProfile"]

    assert profile["isSystemAdministrator"] is True
    assert profile["isEventOrganiser"] is True
    names = [edge["node"]["name"] for edge in profile["projects"]["edges"]]
    assert project1.name in names
    assert project2.name in names


@pytest.mark.parametrize(
    (
        "is_staff",
        "org_kind",
        "has_global_perm",
        "can_see_unpub_third_party_in_admin_project",
        "can_see_unpub_in_other_project",
        "can_administer_third_party",
    ),
    [
        # Case 3: non-staff, system org, group perm
        (False, "system", False, False, False, False),
        # Case 4: non-staff, regular org, group perm
        (False, "regular", False, False, False, False),
        # Case 5: staff, regular org, group perm
        (True, "regular", False, True, False, True),
        # Case 6: staff, no org, global perm
        (True, "none", True, True, True, True),
    ],
    ids=[
        "case_3_system_org_member",
        "case_4_regular_org_member",
        "case_5_staff_with_group_project",
        "case_6_staff_with_global_project_perm",
    ],
)
def test_use_case_event_visibility_and_administration(
    user_api_client,
    is_staff,
    org_kind,
    has_global_perm,
    can_see_unpub_third_party_in_admin_project,
    can_see_unpub_in_other_project,
    can_administer_third_party,
):
    user = user_api_client.user
    user.is_staff = is_staff

    admin_project = ProjectFactory(year=2031, name="Administered Project")
    other_project = ProjectFactory(year=2032, name="Other Project")

    if has_global_perm:
        assign_perm(ProjectPermission.ADMIN.permission_name, user)
    else:
        group = Group.objects.create(name=f"Admin Group for {user.username}")
        assign_perm(ProjectPermission.ADMIN.value, group, admin_project)
        user.groups.add(group)

    if org_kind == "system":
        own_org = OrganisationFactory(name="System Org", is_system=True)
        user.organisations.add(own_org)
    elif org_kind == "regular":
        own_org = OrganisationFactory(name="Own Org")
        user.organisations.add(own_org)
    else:
        own_org = None

    third_party_org = OrganisationFactory(name="Third Party Org")
    user.save()
    user.__dict__.pop("administered_projects", None)

    # Published event in administered project
    EventFactory(
        project=admin_project,
        organisation=third_party_org,
        published_at=timezone.now(),
        name="Pub Event Admin Proj",
    )
    # Unpublished event belonging to third party in administered project
    EventFactory(
        project=admin_project,
        organisation=third_party_org,
        published_at=None,
        name="Unpub Third Party Admin Proj",
    )
    # Unpublished event belonging to own org in administered project
    if own_org:
        EventFactory(
            project=admin_project,
            organisation=own_org,
            published_at=None,
            name="Unpub Own Admin Proj",
        )
    # Events in other project (which user does not administer via group)
    EventFactory(
        project=other_project,
        organisation=third_party_org,
        published_at=timezone.now(),
        name="Pub Event Other Proj",
    )
    EventFactory(
        project=other_project,
        organisation=third_party_org,
        published_at=None,
        name="Unpub Other Proj",
    )

    # 1. Query events in administered project
    executed_admin = user_api_client.execute(
        EVENTS_WITH_ADMIN_QUERY,
        variables={"projectId": get_global_id(admin_project)},
    )
    admin_events_map = {
        edge["node"]["name"]: edge["node"]["canUserAdminister"]
        for edge in executed_admin["data"]["events"]["edges"]
    }

    # Published event in administered project is ALWAYS visible
    assert "Pub Event Admin Proj" in admin_events_map
    assert admin_events_map["Pub Event Admin Proj"] is can_administer_third_party

    # Unpublished event of own org is visible and can be administered
    if own_org:
        assert "Unpub Own Admin Proj" in admin_events_map
        assert admin_events_map["Unpub Own Admin Proj"] is True

    # Unpublished event of third party is only visible to staff (system admin)
    assert (
        "Unpub Third Party Admin Proj" in admin_events_map
    ) is can_see_unpub_third_party_in_admin_project
    if can_see_unpub_third_party_in_admin_project:
        assert (
            admin_events_map["Unpub Third Party Admin Proj"]
            is can_administer_third_party
        )

    # 2. Query events in other project
    executed_other = user_api_client.execute(
        EVENTS_WITH_ADMIN_QUERY,
        variables={"projectId": get_global_id(other_project)},
    )
    other_events = [
        edge["node"]["name"] for edge in executed_other["data"]["events"]["edges"]
    ]

    # Published event in other project is ALWAYS visible
    assert "Pub Event Other Proj" in other_events
    # Unpublished event in other project is only visible if user has global project admin
    assert ("Unpub Other Proj" in other_events) is can_see_unpub_in_other_project

    # 3. Check root organisations query
    executed_orgs = user_api_client.execute(ORGANISATIONS_ROOT_QUERY)
    org_names = [
        edge["node"]["name"] for edge in executed_orgs["data"]["organisations"]["edges"]
    ]
    if is_staff:
        # System administrators see all organisations
        assert third_party_org.name in org_names
    else:
        # Non-staff see only their own organisations
        assert own_org.name in org_names
        assert third_party_org.name not in org_names
