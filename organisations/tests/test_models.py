import pytest
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import RequestFactory

from organisations.admin import OrganisationAdmin
from organisations.factories import OrganisationFactory
from organisations.models import Organisation
from users.factories import UserFactory


@pytest.mark.django_db
def test_system_organisation_unique_constraint():
    OrganisationFactory(name="System Org", is_system=True)
    with pytest.raises((ValidationError, IntegrityError)):
        # Attempt to create another system organisation
        org2 = Organisation(name="Another System Org", is_system=True)
        org2.full_clean()
        org2.save()


@pytest.mark.django_db
def test_multiple_regular_organisations_allowed():
    org1 = OrganisationFactory(name="Org 1", is_system=False)
    org2 = OrganisationFactory(name="Org 2", is_system=False)
    assert org1.id != org2.id
    assert Organisation.objects.filter(is_system=False).count() >= 2


@pytest.mark.django_db
def test_system_organisation_delete_protected():
    system_org = OrganisationFactory(name="Protected System Org", is_system=True)
    with pytest.raises(
        ValidationError, match="The system organisation cannot be deleted."
    ):
        system_org.delete()

    with pytest.raises(
        ValidationError, match="The system organisation cannot be deleted."
    ):
        Organisation.objects.filter(id=system_org.id).delete()

    assert Organisation.objects.filter(id=system_org.id).exists()


@pytest.mark.django_db
def test_regular_organisation_delete_allowed():
    regular_org = OrganisationFactory(name="Deletable Org", is_system=False)
    org_id = regular_org.id
    regular_org.delete()
    assert not Organisation.objects.filter(id=org_id).exists()


@pytest.mark.django_db
def test_system_organisation_flag_clearing_prevented():
    system_org = OrganisationFactory(name="System Org", is_system=True)
    system_org.is_system = False
    with pytest.raises(
        ValidationError, match="The system organisation flag cannot be cleared."
    ):
        system_org.save()

    system_org.refresh_from_db()
    assert system_org.is_system is True


@pytest.mark.django_db
def test_system_organisation_can_be_renamed():
    system_org = OrganisationFactory(is_system=True)
    original_name = system_org.name
    system_org.name = "New System Name"
    system_org.save()
    system_org.refresh_from_db()
    assert system_org.name == "New System Name"
    assert system_org.is_system is True

    # Restore original name
    system_org.name = original_name
    system_org.save()


@pytest.mark.django_db
def test_organisation_admin_protection():
    system_org = OrganisationFactory(name="System Admin Org", is_system=True)
    regular_org = OrganisationFactory(name="Regular Org", is_system=False)

    admin = OrganisationAdmin(Organisation, AdminSite())
    request = RequestFactory().get("/admin")
    request.user = UserFactory(is_superuser=True)

    assert "is_system" in admin.readonly_fields
    assert not admin.has_delete_permission(request, system_org)
    assert admin.has_delete_permission(request, regular_org)


@pytest.mark.django_db
def test_user_can_view_unauthenticated():
    from django.contrib.auth.models import AnonymousUser

    OrganisationFactory(name="Org 1")
    assert Organisation.objects.user_can_view(AnonymousUser()).count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("admin_attr", ["is_staff", "is_superuser"])
def test_user_can_view_system_administrator(admin_attr):
    """System administrators represent all organisations and can view all of them."""
    org1 = OrganisationFactory(name="Org 1", is_system=False)
    org2 = OrganisationFactory(name="Org 2", is_system=False)
    system_org = OrganisationFactory(name="System Org", is_system=True)

    user = UserFactory(**{admin_attr: True})
    viewable = Organisation.objects.user_can_view(user)
    assert org1 in viewable
    assert org2 in viewable
    assert system_org in viewable


@pytest.mark.django_db
def test_user_can_view_regular_user():
    """Regular users (including system organisation members) only see organisations
    they are a member of."""
    system_org = OrganisationFactory(name="System Org", is_system=True)
    my_org = OrganisationFactory(name="My Org", is_system=False)
    other_org = OrganisationFactory(name="Other Org", is_system=False)

    user = UserFactory(is_staff=False, is_superuser=False)
    user.organisations.add(my_org)

    viewable = Organisation.objects.user_can_view(user)
    assert my_org in viewable
    assert other_org not in viewable
    assert system_org not in viewable

    # Member of system organisation only sees system organisation, not all
    system_user = UserFactory(is_staff=False, is_superuser=False)
    system_user.organisations.add(system_org)

    system_viewable = Organisation.objects.user_can_view(system_user)
    assert system_org in system_viewable
    assert my_org not in system_viewable
    assert other_org not in system_viewable
