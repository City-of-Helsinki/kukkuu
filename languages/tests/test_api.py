import pytest

from common.utils import get_global_id
from languages.models import Language


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture(autouse=True)
def languages():
    Language.objects.all().delete()
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


def test_languages_query_orders_special_languages_last(api_client):
    Language.objects.create_from_language_code("zxx")
    Language.objects.create_from_language_code("ara")
    Language.objects.create_option_other()

    executed = api_client.execute(LANGUAGES_QUERY)

    codes = [
        edge["node"]["alpha3Code"] for edge in executed["data"]["languages"]["edges"]
    ]
    assert codes == ["ara", "eng", "swe", "fin", "und", "zxx"]
