import pytest

from common.utils import get_global_id
from languages.consts import SPECIAL_LANGUAGE_ALPHA_3_CODES
from languages.models import Language


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture(autouse=True)
def languages():
    Language.objects.all().delete()
    for code in ("fin", "swe", "eng"):
        Language.objects.create_from_language_code(code)
    Language.objects.create_option_other()
    Language.objects.create_option_speechless()


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


LANGUAGES_FILTER_QUERY = """
query Languages($canBeSpokenAtHome: Boolean, $canBeOccurrenceLanguage: Boolean) {
  languages(
    canBeSpokenAtHome: $canBeSpokenAtHome
    canBeOccurrenceLanguage: $canBeOccurrenceLanguage
  ) {
    edges {
      node {
        alpha3Code
      }
    }
  }
}
"""


@pytest.mark.parametrize(
    "variables, expected_codes",
    [
        ({}, {"eng", "fin", "swe", "und", "zxx"}),
        ({"canBeSpokenAtHome": True}, {"eng", "fin", "swe", "und"}),
        ({"canBeSpokenAtHome": False}, {"zxx"}),
        ({"canBeOccurrenceLanguage": True}, {"eng", "fin", "swe", "zxx"}),
        ({"canBeOccurrenceLanguage": False}, {"und"}),
        (
            {"canBeSpokenAtHome": True, "canBeOccurrenceLanguage": True},
            {"eng", "fin", "swe"},
        ),
        (
            {"canBeSpokenAtHome": True, "canBeOccurrenceLanguage": False},
            {"und"},
        ),
        (
            {"canBeSpokenAtHome": False, "canBeOccurrenceLanguage": True},
            {"zxx"},
        ),
        (
            {"canBeSpokenAtHome": False, "canBeOccurrenceLanguage": False},
            set(),
        ),
    ],
)
def test_languages_query_filters_by_usage_flags(api_client, variables, expected_codes):
    executed = api_client.execute(LANGUAGES_FILTER_QUERY, variables=variables)

    assert {
        edge["node"]["alpha3Code"] for edge in executed["data"]["languages"]["edges"]
    } == expected_codes


def test_languages_query_orders_special_languages_last(api_client):
    Language.objects.create_from_language_code("ara")

    executed = api_client.execute(LANGUAGES_QUERY)

    codes = [
        edge["node"]["alpha3Code"] for edge in executed["data"]["languages"]["edges"]
    ]
    normal_codes = codes[:4]
    special_codes = codes[4:]
    assert not set(normal_codes) & set(SPECIAL_LANGUAGE_ALPHA_3_CODES)
    assert (set(special_codes) & set(SPECIAL_LANGUAGE_ALPHA_3_CODES)) == set(
        special_codes
    )
    assert normal_codes == ["ara", "eng", "swe", "fin"]
    # Not asserting specific order because of collation differences between
    # local test db and CI/CD pipeline, which make sorting differ for these:
    assert set(special_codes) == {"und", "zxx"}
