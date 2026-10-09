import importlib

import pytest
from django.apps import apps
from django.conf import settings
from guardian.shortcuts import assign_perm

from organisations.models import Organisation
from projects.enums import ProjectPermission
from projects.factories import ProjectFactory
from users.factories import UserFactory

migration_module = importlib.import_module(
    "events.migrations.0032_populate_event_organisation"
)
populate_events_and_admins = migration_module.populate_events_and_admins
reverse_populate = migration_module.reverse_populate


@pytest.mark.django_db
def test_populate_event_organisation_migration_forward_and_reverse():
    default_name = getattr(
        settings, "KUKKUU_DEFAULT_ORGANISATION_NAME", "Hekla (system)"
    )
    default_org, _ = Organisation.objects.get_or_create(name=default_name)
    project = ProjectFactory()

    staff_user = UserFactory(is_staff=True)
    admin_perm_user = UserFactory()
    assign_perm(ProjectPermission.ADMIN.value, admin_perm_user, project)
    publish_perm_user = UserFactory()
    assign_perm(ProjectPermission.PUBLISH.value, publish_perm_user, project)
    regular_user = UserFactory()

    # Ensure none are in default_org initially
    default_org.users.clear()

    # Run forward migration
    populate_events_and_admins(apps, None)

    assert default_org.users.filter(id=staff_user.id).exists()
    assert default_org.users.filter(id=admin_perm_user.id).exists()
    assert default_org.users.filter(id=publish_perm_user.id).exists()
    assert not default_org.users.filter(id=regular_user.id).exists()

    # Run reverse migration
    reverse_populate(apps, None)

    assert default_org.users.count() == 0
