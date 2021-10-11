import pytest

from common.utils import get_global_id
from languages.models import Language


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture(autouse=True)
def languages():
    for code in ("fin", "swe", "eng"):
        Language.objects.create_from_language_code(code)


LANGUAGES_QUERY = """
query Languages {
  languages {
    edges {
      node {
        alpha3Code
        name
        translations {
          languageCode
          name
        }
      }
    }
  }
}
"""

LANGUAGE_QUERY = """
query Language($id: ID!) {
  language(id: $id){
    alpha3Code
    name
    translations {
      languageCode
      name
    }
  }
}
"""


def test_languages_query(snapshot, api_client):
    executed = api_client.execute(LANGUAGES_QUERY)

    snapshot.assert_match(executed)


def test_language_query(snapshot, api_client):
    variables = {"id": get_global_id(Language.objects.get(alpha_3_code="fin"))}

    executed = api_client.execute(LANGUAGE_QUERY, variables=variables)

    snapshot.assert_match(executed)
