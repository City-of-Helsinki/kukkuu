import pytest
from django.conf import settings
from graphql_relay import to_global_id

from common.tests.utils import assert_permission_denied
from organisations.factories import OrganisationFactory
from organisations.models import Organisation

ORGANISATIONS_QUERY = """
query Organisations {
  organisations {
    edges {
      node {
        id
        name
      }
    }
  }
}
"""

ORGANISATION_QUERY = """
query Organisation($id: ID!) {
  organisation(id: $id) {
    id
    name
  }
}
"""


@pytest.mark.django_db
def test_organisations_query_unauthenticated(api_client):
    """
    Test that unauthenticated requests to the organisations query are denied.
    """
    executed = api_client.execute(ORGANISATIONS_QUERY)
    assert_permission_denied(executed)


@pytest.mark.django_db
def test_organisations_query_normal_user(user_api_client):
    """
    Test that regular authenticated users without administrative privileges
    receive an empty organisation list.
    """
    OrganisationFactory.create_batch(3)
    executed = user_api_client.execute(ORGANISATIONS_QUERY)
    assert executed.get("errors") is None
    assert executed["data"]["organisations"]["edges"] == []


@pytest.mark.django_db
def test_organisations_query_system_admin(project_user_api_client):
    """
    Test that a system administrator (member of the default organisation)
    can query all organisations in the system.
    """
    system_org, _ = Organisation.objects.get_or_create(
        name=settings.KUKKUU_DEFAULT_ORGANISATION_NAME
    )
    project_user_api_client.user.organisations.add(system_org)

    OrganisationFactory(name="First Organisation")
    OrganisationFactory(name="Second Organisation")

    executed = project_user_api_client.execute(ORGANISATIONS_QUERY)
    assert executed.get("errors") is None
    org_names = [
        edge["node"]["name"] for edge in executed["data"]["organisations"]["edges"]
    ]
    assert "First Organisation" in org_names
    assert "Second Organisation" in org_names


@pytest.mark.django_db
def test_organisations_query_project_admin(project_user_api_client, project):
    """
    Test that a project admin who is not a system administrator can only see
    the organisations they are explicitly a member of, and not other organisations.
    """
    my_org = OrganisationFactory(name="My Organisation")
    OrganisationFactory(name="Other Organisation")
    project_user_api_client.user.organisations.set([my_org])

    executed = project_user_api_client.execute(ORGANISATIONS_QUERY)
    assert executed.get("errors") is None
    org_names = [
        edge["node"]["name"] for edge in executed["data"]["organisations"]["edges"]
    ]
    assert "My Organisation" in org_names
    assert "Other Organisation" not in org_names


@pytest.mark.django_db
def test_single_organisation_query(project_user_api_client):
    """
    Test querying a single organisation by its Relay ID as a system administrator.
    """
    system_org, _ = Organisation.objects.get_or_create(
        name=settings.KUKKUU_DEFAULT_ORGANISATION_NAME
    )
    project_user_api_client.user.organisations.add(system_org)
    org = OrganisationFactory(name="Single Org")

    variables = {"id": to_global_id("OrganisationNode", org.id)}
    executed = project_user_api_client.execute(ORGANISATION_QUERY, variables=variables)
    assert executed.get("errors") is None
    assert executed["data"]["organisation"]["name"] == "Single Org"


@pytest.mark.django_db
def test_organisations_query_staff_user(project_user_api_client):
    """
    Test that a staff user (is_staff=True) is treated as a system administrator
    and can query all organisations, including external ones they are not a member of.
    """
    user = project_user_api_client.user
    user.is_staff = True
    user.save()

    own_org = OrganisationFactory(name="User Own Organisation")
    external_org = OrganisationFactory(name="External Organisation")
    user.organisations.set([own_org])

    executed = project_user_api_client.execute(ORGANISATIONS_QUERY)
    assert executed.get("errors") is None
    org_names = [
        edge["node"]["name"] for edge in executed["data"]["organisations"]["edges"]
    ]
    assert own_org.name in org_names
    assert external_org.name in org_names
