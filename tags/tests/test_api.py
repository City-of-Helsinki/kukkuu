import pytest
from django.utils import translation

from common.utils import get_global_id
from tags.factories import ThemePathFactory
from tags.models import ThemePath

THEME_PATHS_QUERY = """
query ThemePaths {
  themePaths {
    edges {
      node {
        slug
        name
        description
        sortOrder
        translations {
          languageCode
          name
          description
        }
      }
    }
  }
}
"""

THEME_PATH_QUERY = """
query ThemePath($id: ID!) {
  themePath(id: $id) {
    slug
    name
    description
    sortOrder
    translations {
      languageCode
      name
      description
    }
  }
}
"""

RHYTHM_NODE = {
    "slug": "rhythm",
    "name": "Rytmi",
    "description": "Kuvaus",
    "sortOrder": 1,
    "translations": [
        {"languageCode": "EN", "name": "Rhythm", "description": "Description"},
        {"languageCode": "FI", "name": "Rytmi", "description": "Kuvaus"},
        {"languageCode": "SV", "name": "Rytm", "description": "Beskrivning"},
    ],
}


@pytest.fixture(autouse=True)
def only_test_theme_paths(db):
    ThemePath.objects.all().delete()


@pytest.fixture
def rhythm_theme_path():
    theme_path = ThemePathFactory(
        slug="rhythm", name="Rytmi", description="Kuvaus", sort_order=1
    )
    theme_path.create_translation("sv", name="Rytm", description="Beskrivning")
    theme_path.create_translation("en", name="Rhythm", description="Description")
    return theme_path


def _query_theme_path_nodes(api_client):
    executed = api_client.execute(THEME_PATHS_QUERY)
    return [edge["node"] for edge in executed["data"]["themePaths"]["edges"]]


def test_theme_paths_query_is_public_and_ordered_by_sort_order_then_slug(api_client):
    ThemePathFactory(slug="no_order", sort_order=None)
    ThemePathFactory(slug="b", sort_order=2)
    ThemePathFactory(slug="a", sort_order=2)
    ThemePathFactory(slug="first", sort_order=1)

    nodes = _query_theme_path_nodes(api_client)

    assert [node["slug"] for node in nodes] == ["first", "a", "b", "no_order"]


def test_theme_paths_query_returns_translations(api_client, rhythm_theme_path):
    story = ThemePathFactory(
        slug="story", name="Tarina", description="Esitys", sort_order=2
    )
    story.create_translation("sv", name="Berättelse", description="Föreställning")

    nodes = _query_theme_path_nodes(api_client)

    assert nodes == [
        RHYTHM_NODE,
        {
            "slug": "story",
            "name": "Tarina",
            "description": "Esitys",
            "sortOrder": 2,
            "translations": [
                {"languageCode": "FI", "name": "Tarina", "description": "Esitys"},
                {
                    "languageCode": "SV",
                    "name": "Berättelse",
                    "description": "Föreställning",
                },
            ],
        },
    ]


@pytest.mark.parametrize(
    ("language", "expected_name", "expected_description"),
    [
        ("fi", "Rytmi", "Kuvaus"),
        ("sv", "Rytm", "Beskrivning"),
        ("en", "Rhythm", "Description"),
    ],
)
def test_theme_path_name_and_description_use_active_language(
    api_client, rhythm_theme_path, language, expected_name, expected_description
):
    with translation.override(language):
        nodes = _query_theme_path_nodes(api_client)

    assert nodes[0]["name"] == expected_name
    assert nodes[0]["description"] == expected_description


def test_theme_path_name_and_description_fall_back_when_active_language_missing(
    api_client,
):
    theme_path = ThemePath.objects.create(slug="only_sv")
    theme_path.create_translation("sv", name="Namn", description="Beskrivning")

    nodes = _query_theme_path_nodes(api_client)

    assert nodes[0]["name"] == "Namn"
    assert nodes[0]["description"] == "Beskrivning"


def test_theme_path_name_is_slug_and_description_empty_without_translations(
    api_client,
):
    ThemePath.objects.create(slug="no_translations")

    nodes = _query_theme_path_nodes(api_client)

    assert nodes[0]["translations"] == []
    assert nodes[0]["name"] == "no_translations"
    assert nodes[0]["description"] == ""


def test_theme_path_query_by_id(api_client, rhythm_theme_path):
    executed = api_client.execute(
        THEME_PATH_QUERY, variables={"id": get_global_id(rhythm_theme_path)}
    )

    assert executed["data"]["themePath"] == RHYTHM_NODE
