import pytest

from children.factories import ChildWithGuardianFactory
from gdpr.consts import CLEARED_VALUE
from gdpr.service import clear_data


@pytest.mark.django_db
def test_clear_data_service():
    child = ChildWithGuardianFactory(name="Karate Kid")
    guardian = child.guardians.all().first()
    user = guardian.user
    clear_data(user=user, dry_run=False)
    user.refresh_from_db()
    guardian.refresh_from_db()
    child.refresh_from_db()
    assert user.first_name == ""
    assert user.last_name == ""
    assert user.username
    assert guardian.first_name == CLEARED_VALUE
    assert guardian.last_name == CLEARED_VALUE
    assert child.name == ""
