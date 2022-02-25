import pytest

from kukkuu.service import get_hashid_service


@pytest.fixture
def hashids():
    return get_hashid_service()
