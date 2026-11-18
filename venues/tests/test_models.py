from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import RequestFactory

from users.factories import UserFactory
from venues.admin import VenueAdmin
from venues.factories import SystemVenueFactory, VenueFactory
from venues.models import Venue
from venues.services import get_system_venue


@pytest.mark.django_db
def test_venue_creation(project):
    """Verify regular project venue creation and default is_system=False."""
    VenueFactory(project=project)
    assert Venue.objects.filter(is_system=False).count() == 1


@pytest.mark.django_db
def test_system_venue_unique_constraint():
    """Verify database unique constraint permits only one system venue."""
    SystemVenueFactory()
    with pytest.raises(ValidationError, match="There can be only one system venue."):
        venue2 = Venue(is_system=True, project=None)
        venue2.save()


@pytest.mark.django_db
def test_system_venue_check_constraint_cannot_have_project(project):
    """Verify check constraint rejects a system venue with a project assignment."""
    with pytest.raises(
        ValidationError, match="System venue cannot belong to a project."
    ):
        venue = Venue(is_system=True, project=project)
        venue.save()


@pytest.mark.django_db
def test_regular_venue_check_constraint_must_have_project():
    """Verify check constraint requires regular venues to belong to a project."""
    with pytest.raises(
        ValidationError, match="Regular venue must belong to a project."
    ):
        venue = Venue(is_system=False, project=None)
        venue.save()


@pytest.mark.django_db
def test_multiple_regular_venues_allowed(project):
    """Verify multiple regular venues can be created within the same project."""
    v1 = VenueFactory(project=project)
    v2 = VenueFactory(project=project)
    assert v1.id != v2.id
    assert Venue.objects.filter(is_system=False).count() >= 2


@pytest.mark.django_db
def test_system_venue_delete_protected():
    """Verify system venue is protected against deletion on instance and queryset levels."""
    system_venue = SystemVenueFactory()
    with pytest.raises(ValidationError, match="The system venue cannot be deleted."):
        system_venue.delete()

    with pytest.raises(ValidationError, match="The system venue cannot be deleted."):
        Venue.objects.filter(id=system_venue.id).delete()

    regular_venue = VenueFactory()
    venues = Venue.objects.filter(id__in=[system_venue.id, regular_venue.id])
    assert venues.count() >= 2

    # Test that system venue can not be deleted as part of a larger queryset
    with pytest.raises(ValidationError, match="The system venue cannot be deleted."):
        venues.delete()

    assert Venue.objects.filter(id=system_venue.id).exists()
    # The whole queryset's deletion should have been prevented:
    assert Venue.objects.filter(id=regular_venue.id).exists()


@pytest.mark.django_db
def test_regular_venue_delete_allowed(project):
    """Verify regular venues can be deleted normally."""
    regular_venue = VenueFactory(project=project)
    v_id = regular_venue.id
    regular_venue.delete()
    assert not Venue.objects.filter(id=v_id).exists()


@pytest.mark.django_db
def test_system_venue_flag_clearing_prevented(project):
    """Verify clearing the is_system flag on an existing system venue is rejected."""
    system_venue = SystemVenueFactory()
    system_venue.is_system = False
    with pytest.raises(
        ValidationError, match="The system venue flag cannot be cleared."
    ):
        system_venue.save()

    system_venue.refresh_from_db()
    assert system_venue.is_system is True
    assert system_venue.project is None


@pytest.mark.django_db
def test_system_venue_project_assignment_prevented(project):
    """Verify assigning a system venue to a project is rejected."""
    system_venue = SystemVenueFactory()
    system_venue.project = project
    with pytest.raises(
        ValidationError, match="System venue cannot belong to a project."
    ):
        system_venue.save()

    system_venue.refresh_from_db()
    assert system_venue.is_system is True
    assert system_venue.project is None


@pytest.mark.django_db
def test_system_venue_str():
    """Verify string representations for system venue and project-associated venues."""
    system_venue = SystemVenueFactory()
    assert system_venue.project is None
    assert (
        str(system_venue) == f"{settings.KUKKUU_DEFAULT_VENUE_NAME} ({system_venue.pk})"
    )

    regular_venue = VenueFactory()
    assert regular_venue.project is not None
    assert f"({regular_venue.project.year})" in str(regular_venue)


@pytest.mark.django_db
def test_system_venue_can_user_administer(project):
    """Verify only staff/superusers have administration rights over the system venue."""
    system_venue = SystemVenueFactory()
    regular_venue = VenueFactory(project=project)

    superuser = UserFactory(is_staff=False, is_superuser=True)
    staff_user = UserFactory(is_staff=True, is_superuser=False)
    project_admin = UserFactory()
    project_admin.administered_projects = [project]
    regular_user = UserFactory()

    assert system_venue.can_user_administer(superuser) is True
    assert system_venue.can_user_administer(staff_user) is True
    assert system_venue.can_user_administer(project_admin) is False
    assert system_venue.can_user_administer(regular_user) is False

    assert regular_venue.can_user_administer(superuser) is True
    assert regular_venue.can_user_administer(staff_user) is False
    assert regular_venue.can_user_administer(project_admin) is True
    assert regular_venue.can_user_administer(regular_user) is False


@pytest.mark.django_db
def test_venue_admin_protection(project):
    """Verify Django admin displays, read-only constraints, and delete protection for system venues."""
    system_venue = SystemVenueFactory()
    regular_venue = VenueFactory(project=project)

    admin = VenueAdmin(Venue, AdminSite())
    request = RequestFactory().get("/admin")
    request.user = UserFactory(is_superuser=True)

    assert "is_system" in admin.readonly_fields
    assert not admin.has_delete_permission(request, system_venue)
    assert admin.has_delete_permission(request, regular_venue)
    assert admin.get_project_year(system_venue) == "-"
    assert admin.get_project_year(regular_venue) == project.year


@pytest.mark.django_db
def test_get_system_venue_helper(project):
    """Verify get_system_venue helper creates the system venue and subsequent calls are idempotent."""
    Venue.objects.filter(is_system=True).update(project_id=project.id, is_system=False)
    Venue.objects.all().delete()
    assert not Venue.objects.filter(is_system=True).exists()

    venue = get_system_venue()
    assert venue.is_system is True
    assert venue.project is None
    assert venue.name == settings.KUKKUU_DEFAULT_VENUE_NAME

    # Second call returns existing
    venue2 = get_system_venue()
    assert venue2.id == venue.id
    assert Venue.objects.filter(is_system=True).count() == 1


@pytest.mark.django_db
def test_get_system_venue_concurrent_creation_recovery(project):
    """Verify get_system_venue recovers if concurrent creation occurs."""
    Venue.objects.filter(is_system=True).update(project_id=project.id, is_system=False)
    Venue.objects.all().delete()

    first_call = True
    real_filter = Venue.objects.filter

    def mock_filter(*args, **kwargs):
        nonlocal first_call
        if kwargs.get("is_system") is True and first_call:
            first_call = False
            return Venue.objects.none()
        return real_filter(*args, **kwargs)

    created_venue = Venue.objects.create_translatable_object(
        is_system=True,
        project=None,
        translations=[
            {
                "language_code": lang_code,
                "name": settings.KUKKUU_DEFAULT_VENUE_NAME,
            }
            for lang_code in settings.PARLER_SUPPORTED_LANGUAGE_CODES
        ],
    )

    with patch.object(
        Venue.objects,
        "filter",
        side_effect=mock_filter,
    ):
        venue = get_system_venue()

    assert venue.id == created_venue.id
    assert venue.is_system is True


@pytest.mark.django_db
def test_get_system_venue_unrelated_error_propagates(project):
    Venue.objects.filter(is_system=True).update(project_id=project.id, is_system=False)
    Venue.objects.all().delete()

    with patch.object(
        Venue.objects,
        "create_translatable_object",
        side_effect=IntegrityError("other error"),
    ):
        with pytest.raises(IntegrityError):
            get_system_venue()
