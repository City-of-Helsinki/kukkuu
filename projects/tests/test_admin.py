import pytest

from organisations.factories import OrganisationFactory
from projects.admin import UserSelectForm
from users.factories import UserFactory


@pytest.mark.django_db
def test_user_select_form_uses_system_administrators():
    """
    Test that UserSelectForm filters choices to system administrators.
    """
    system_org = OrganisationFactory(is_system=True)
    staff_user = UserFactory(is_staff=True)
    org_user = UserFactory()
    org_user.organisations.add(system_org)
    regular_user = UserFactory(is_staff=False, is_superuser=False)

    form = UserSelectForm()
    choices = list(form.fields["user"].queryset)

    assert staff_user in choices
    assert org_user not in choices
    assert regular_user not in choices
