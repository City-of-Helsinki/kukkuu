from unittest.mock import patch

import pytest
from django.test import RequestFactory
from graphql import ExecutionResult, GraphQLError

from kukkuu.consts import GENERAL_ERROR
from kukkuu.views import SentryGraphQLView

SENTRY_CAPTURE_EXCEPTION = "sentry_sdk.capture_exception"


@pytest.mark.parametrize(
    "query,expected_error_substring",
    [
        (
            "query { nonExistentField }",
            "Cannot query field 'nonExistentField' on type 'Query'.",
        ),
        (
            "query { languages { edges { node { nonExistentField } } } }",
            "Cannot query field 'nonExistentField' on type 'LanguageNode'.",
        ),
        (
            "query { languages(unknownArg: true) { edges { node { id } } } }",
            "Unknown argument 'unknownArg' on field 'Query.languages'.",
        ),
        (
            "query UnusedVar($unused: ID) { __typename }",
            "Variable '$unused' is never used in operation 'UnusedVar'.",
        ),
        (
            "query {",
            "Syntax Error:",
        ),
    ],
)
def test_graphql_invalid_queries_return_400_without_sentry(
    client, query, expected_error_substring
):
    with patch(SENTRY_CAPTURE_EXCEPTION) as mock_sentry:
        response = client.post(
            "/graphql",
            {"query": query},
            content_type="application/json",
        )

    assert response.status_code == 400
    payload = response.json()
    assert "data" not in payload
    assert any(expected_error_substring in err["message"] for err in payload["errors"])
    assert payload["errors"][0]["extensions"] == {"code": GENERAL_ERROR}
    mock_sentry.assert_not_called()


def test_graphql_depth_limit_returns_400_without_sentry(client, settings):
    settings.KUKKUU_QUERY_MAX_DEPTH = 2
    query = "query Deep { languages { edges { node { id } } } }"

    with patch(SENTRY_CAPTURE_EXCEPTION) as mock_sentry:
        response = client.post(
            "/graphql",
            {"query": query},
            content_type="application/json",
        )

    assert response.status_code == 400
    payload = response.json()
    assert (
        "'Deep' exceeds maximum operation depth of 2."
        in payload["errors"][0]["message"]
    )
    mock_sentry.assert_not_called()


@pytest.mark.django_db
def test_graphql_valid_query_returns_200(client):
    with patch(SENTRY_CAPTURE_EXCEPTION) as mock_sentry:
        response = client.post(
            "/graphql",
            {"query": "query { languages { edges { node { id name } } } }"},
            content_type="application/json",
        )

    assert response.status_code == 200
    payload = response.json()
    assert "errors" not in payload
    assert len(payload["data"]["languages"]["edges"]) > 0
    mock_sentry.assert_not_called()


def test_sentry_captures_execution_graphql_error_without_original_error():
    """Execution GraphQLErrors with a path and no original_error (e.g. non-null
    field violations) should report the GraphQLError itself, never None."""
    request = RequestFactory().post("/graphql")
    execution_error = GraphQLError(
        "Cannot return null for non-nullable field Query.someField.",
        path=["someField"],
    )
    view = SentryGraphQLView()

    with (
        patch.object(
            SentryGraphQLView.__bases__[0],
            "execute_graphql_request",
            return_value=ExecutionResult(data=None, errors=[execution_error]),
        ),
        patch(SENTRY_CAPTURE_EXCEPTION) as mock_sentry,
    ):
        view.execute_graphql_request(request, data={}, query="{ someField }")

    mock_sentry.assert_called_once_with(execution_error)
