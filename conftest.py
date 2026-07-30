import pytest


@pytest.fixture(autouse=True)
def use_local_file_storage(settings):
    """Force local filesystem storage for tests.

    Developers may configure a remote storage backend (e.g. Azure) via their
    local `.env` for manual testing against real infrastructure. Tests should
    not depend on that configuration, so it's overridden here to keep test
    runs deterministic and independent of the developer's environment.
    """
    settings.STORAGES = {
        **settings.STORAGES,
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    }
