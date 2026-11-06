from dataclasses import dataclass

import pytest
from django.utils import translation
from factory.django import DjangoModelFactory

from common.utils import get_global_id
from tags.factories import AccessibilityFactory, ThemePathFactory
from tags.models import Accessibility, Tag, ThemePath

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

ACCESSIBILITIES_QUERY = """
query Accessibilities {
  accessibilities {
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

ACCESSIBILITY_QUERY = """
query Accessibility($id: ID!) {
  accessibility(id: $id) {
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


@dataclass(frozen=True)
class TagApi:
    """GraphQL test configuration for one tag model.

    Attributes:
        model: The tag model. Its rows are deleted before each test to remove
            the rows seeded by migrations.
        factory: Factory that creates instances of `model`.
        list_query: Query string that fetches the connection of every
            instance of `model`.
        list_field: Root field name used in `list_query`, e.g. "themePaths".
            The tests read the result from `data[list_field]`.
        node_query: Query string that fetches one instance of `model` by
            global ID with the variable `$id`.
        node_field: Root field name used in `node_query`, e.g. "themePath".
            The tests read the result from `data[node_field]`.
    """

    model: type[Tag]
    factory: type[DjangoModelFactory]
    list_query: str
    list_field: str
    node_query: str
    node_field: str


THEME_PATH_API = TagApi(
    model=ThemePath,
    factory=ThemePathFactory,
    list_query=THEME_PATHS_QUERY,
    list_field="themePaths",
    node_query=THEME_PATH_QUERY,
    node_field="themePath",
)

ACCESSIBILITY_API = TagApi(
    model=Accessibility,
    factory=AccessibilityFactory,
    list_query=ACCESSIBILITIES_QUERY,
    list_field="accessibilities",
    node_query=ACCESSIBILITY_QUERY,
    node_field="accessibility",
)

TEST_TRANSLATIONS = {
    "fi": {"name": "Nimi", "description": "Kuvaus"},
    "sv": {"name": "Namn", "description": "Beskrivning"},
    "en": {"name": "Name", "description": "Description"},
}

TEST_TAG = {"slug": "test", "sort_order": 1, "translations": TEST_TRANSLATIONS}

TEST_NODE = {
    "slug": TEST_TAG["slug"],
    "name": TEST_TRANSLATIONS["fi"]["name"],
    "description": TEST_TRANSLATIONS["fi"]["description"],
    "sortOrder": TEST_TAG["sort_order"],
    "translations": [
        {"languageCode": code.upper(), **fields}
        for code, fields in sorted(TEST_TRANSLATIONS.items())
    ],
}


@pytest.fixture(
    params=[THEME_PATH_API, ACCESSIBILITY_API], ids=["theme_path", "accessibility"]
)
def tag_api(request):
    return request.param


@pytest.fixture(autouse=True)
def only_test_tags(db, tag_api):
    tag_api.model.objects.all().delete()


@pytest.fixture
def tag(tag_api):
    return tag_api.factory(**TEST_TAG)


def _query_nodes(api_client, tag_api):
    executed = api_client.execute(tag_api.list_query)
    return [edge["node"] for edge in executed["data"][tag_api.list_field]["edges"]]


def test_tags_query_is_public_and_ordered_by_sort_order_then_slug(api_client, tag_api):
    tag_api.factory(slug="no_order", sort_order=None)
    tag_api.factory(slug="b", sort_order=2)
    tag_api.factory(slug="a", sort_order=2)
    tag_api.factory(slug="first", sort_order=1)

    nodes = _query_nodes(api_client, tag_api)

    assert [node["slug"] for node in nodes] == ["first", "a", "b", "no_order"]


def test_tags_query_returns_translations(api_client, tag_api, tag):
    tag_api.factory(
        slug="second",
        sort_order=2,
        translations={
            "fi": {"name": "Toinen", "description": "Esitys"},
            "sv": {"name": "Andra", "description": "Föreställning"},
        },
    )

    nodes = _query_nodes(api_client, tag_api)

    assert nodes == [
        TEST_NODE,
        {
            "slug": "second",
            "name": "Toinen",
            "description": "Esitys",
            "sortOrder": 2,
            "translations": [
                {"languageCode": "FI", "name": "Toinen", "description": "Esitys"},
                {
                    "languageCode": "SV",
                    "name": "Andra",
                    "description": "Föreställning",
                },
            ],
        },
    ]


@pytest.mark.parametrize("language", TEST_TRANSLATIONS)
def test_tag_name_and_description_use_active_language(
    api_client, tag_api, tag, language
):
    with translation.override(language):
        nodes = _query_nodes(api_client, tag_api)

    assert nodes[0]["name"] == TEST_TRANSLATIONS[language]["name"]
    assert nodes[0]["description"] == TEST_TRANSLATIONS[language]["description"]


def test_tag_name_and_description_fall_back_when_active_language_missing(
    api_client, tag_api
):
    tag = tag_api.model.objects.create(slug="only_sv")
    tag.create_translation("sv", name="Namn", description="Beskrivning")

    nodes = _query_nodes(api_client, tag_api)

    assert nodes[0]["name"] == "Namn"
    assert nodes[0]["description"] == "Beskrivning"


def test_tag_name_is_slug_and_description_empty_without_translations(
    api_client, tag_api
):
    tag_api.model.objects.create(slug="no_translations")

    nodes = _query_nodes(api_client, tag_api)

    assert nodes[0]["translations"] == []
    assert nodes[0]["name"] == "no_translations"
    assert nodes[0]["description"] == ""


def test_tag_query_by_id(api_client, tag_api, tag):
    executed = api_client.execute(
        tag_api.node_query, variables={"id": get_global_id(tag)}
    )

    assert executed["data"][tag_api.node_field] == TEST_NODE
