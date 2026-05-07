from unittest.mock import patch

import pytest
from django.conf import settings
from django.test import override_settings
from django.utils.module_loading import import_string
from storages.backends.azure_storage import AzureStorage

from utils.storage import AzureStorageWithoutQuerystringAuth

SAS_URL = (
    "https://myaccount.blob.core.windows.net/mycontainer/myfile.jpg"
    "?sv=2021-06-08&se=2026-01-01T00%3A00%3A00Z&sr=b&sp=r&sig=FAKESIG"
)
CLEAN_URL = "https://myaccount.blob.core.windows.net/mycontainer/myfile.jpg"


def _make_storage(model=AzureStorageWithoutQuerystringAuth, **overrides):
    """Return an AzureStorageWithoutQuerystringAuth with minimal required settings."""
    kwargs = dict(
        account_name="myaccount",
        account_key="123454567",
        azure_container="mycontainer",
        expiration_secs=3600,
    )
    kwargs.update(overrides)
    return model(**kwargs)


@pytest.mark.parametrize(
    "model, expected_url",
    [
        (AzureStorage, SAS_URL),
        (AzureStorageWithoutQuerystringAuth, CLEAN_URL),
    ],
)
@patch.object(AzureStorage, "url", return_value=SAS_URL)
def test_url_querystring_auth(mock_url, model, expected_url):
    storage = _make_storage(model=model)
    result = storage.url("myfile.jpg")

    assert result == expected_url


@patch.object(AzureStorage, "url", return_value=SAS_URL)
def test_url_querystring_auth_false_no_query_string_in_parent_url(mock_url):
    storage = _make_storage()
    result = storage.url("myfile.jpg")

    assert result == CLEAN_URL
    assert "?" not in result


@override_settings(
    STORAGES_DEFAULT_BACKEND="utils.storage.AzureStorageWithoutQuerystringAuth"
)
def test_default_storage_uses_azure_without_querystring_auth():
    backend_class = import_string(settings.STORAGES_DEFAULT_BACKEND)
    assert issubclass(backend_class, AzureStorage)
    assert backend_class is AzureStorageWithoutQuerystringAuth
