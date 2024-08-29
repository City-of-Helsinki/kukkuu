import pytest
from graphql_relay import to_global_id

from common.tests.utils import assert_permission_denied


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


PROJECTS_QUERY = """
query Projects {
  projects {
    edges {
      node {
        id
        name
        year
        translations {
          languageCode
          name
        }
        singleEventsAllowed
        enrolmentLimit
      }
    }
  }
}
"""

PROJECT_QUERY = """
query Project($id: ID!) {
  project(id: $id){
    id
    name
    year
    translations {
      languageCode
      name
    }
    singleEventsAllowed
    enrolmentLimit
  }
}
"""


def test_projects_query_unauthenticated(api_client, project):
    executed = api_client.execute(PROJECTS_QUERY)

    assert_permission_denied(executed)


def test_project_query_unauthenticated(snapshot, api_client, project):
    variables = {"id": to_global_id("ProjectNode", project.id)}

    executed = api_client.execute(PROJECT_QUERY, variables=variables)

    assert_permission_denied(executed)


def test_projects_query_normal_user(snapshot, guardian_api_client, project):
    executed = guardian_api_client.execute(PROJECTS_QUERY)
    assert len(executed["data"]["projects"]["edges"]) == 1
    snapshot.assert_match(executed)


def test_project_query_normal_user(snapshot, guardian_api_client, project):
    variables = {"id": to_global_id("ProjectNode", project.id)}

    executed = guardian_api_client.execute(PROJECT_QUERY, variables=variables)
    snapshot.assert_match(executed)
