import pytest
from django.conf import settings

from organisations.factories import OrganisationFactory
from projects.admin import UserSelectForm
from users.factories import UserFactory


@pytest.mark.django_db
def test_user_select_form_uses_system_administrators():
    """
    Test that UserSelectForm filters choices to system administrators.
    """
    default_org = OrganisationFactory(name=settings.KUKKUU_DEFAULT_ORGANISATION_NAME)
    staff_user = UserFactory(is_staff=True)
    org_user = UserFactory()
    org_user.organisations.add(default_org)
    regular_user = UserFactory(is_staff=False, is_superuser=False)

    form = UserSelectForm()
    choices = list(form.fields["user"].queryset)

    assert staff_user in choices
    assert org_user in choices
    assert regular_user not in choices
