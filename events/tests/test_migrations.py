import importlib

import pytest
from django.apps import apps
from django.conf import settings
from django.db import migrations
from guardian.shortcuts import assign_perm

from events.factories import EventFactory
from events.models import Event
from organisations.models import Organisation
from projects.enums import ProjectPermission
from projects.factories import ProjectFactory
from users.factories import UserFactory

migration_module = importlib.import_module(
    "events.migrations.0032_populate_event_organisation"
)
populate_events_and_admins = migration_module.populate_events_and_admins
reverse_populate = migration_module.reverse_populate

migration_0035_module = importlib.import_module(
    "events.migrations.0035_add_enrolment_extra_participants"
)
replace_child_and_1_or_2_guardians_with_family = (
    migration_0035_module.replace_child_and_1_or_2_guardians_with_family
)
Migration0035 = migration_0035_module.Migration


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


@pytest.mark.django_db
def test_populate_event_organisation_migration_missing_org_raises():
    default_name = getattr(
        settings, "KUKKUU_DEFAULT_ORGANISATION_NAME", "Hekla (system)"
    )
    Organisation.objects.filter(name=default_name).update(is_system=False)
    Organisation.objects.filter(name=default_name).delete()

    with pytest.raises(RuntimeError, match="Default organisation not found"):
        populate_events_and_admins(apps, None)


@pytest.mark.django_db
def test_migrate_child_and_1_or_2_guardians_to_family():
    event = EventFactory(participants_per_invite="child_and_1_or_2_guardians")
    assert (
        Event.objects.filter(
            participants_per_invite="child_and_1_or_2_guardians"
        ).count()
        == 1
    )

    replace_child_and_1_or_2_guardians_with_family(apps, None)

    event.refresh_from_db()
    assert event.participants_per_invite == "family"
    assert (
        Event.objects.filter(
            participants_per_invite="child_and_1_or_2_guardians"
        ).count()
        == 0
    )

    migration_instance = Migration0035(
        "0035_add_enrolment_extra_participants", "events"
    )
    run_python_op = migration_instance.operations[0]
    assert run_python_op.reverse_code is migrations.RunPython.noop
