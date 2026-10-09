import logging

from django.conf import settings
from django.db import migrations

logger = logging.getLogger(__name__)


def _get_default_organisation(apps):
    """
    Retrieves the default system organisation configured in settings.
    """
    Organisation = apps.get_model("organisations", "Organisation")
    default_name = getattr(
        settings, "KUKKUU_DEFAULT_ORGANISATION_NAME", "Kukkuu system"
    )
    return Organisation.objects.filter(name=default_name).first()


def _assign_organisation_to_events(apps, org):
    """
    Updates all existing events that do not have an organisation assigned,
    setting them to the provided default organisation.
    """
    Event = apps.get_model("events", "Event")
    events_updated = Event.objects.filter(organisation__isnull=True).update(
        organisation=org
    )
    logger.info(f"Assigned default organisation to {events_updated} existing events.")


def _assign_organisation_to_staff_users(apps, org):
    """
    Iterates over all existing staff users and assigns them to the default
    organisation to preserve their administration privileges.
    """
    User = apps.get_model("users", "User")
    staff_users = User.objects.filter(is_staff=True)
    count = 0
    for user in staff_users:
        user.organisations.add(org)
        count += 1
    logger.info(f"Assigned default organisation to {count} existing staff users.")


def populate_events_and_admins(apps, schema_editor):
    """
    Main migration runner to assign the default system organisation to existing
    events and staff users.
    """
    org = _get_default_organisation(apps)
    if not org:
        logger.error(
            "Default organisation not found. Ensure organisations migration 0002 has run."
        )
        return

    _assign_organisation_to_events(apps, org)
    _assign_organisation_to_staff_users(apps, org)


def reverse_populate(apps, schema_editor):
    # It's not safe to automatically set organisation back to null if the model is going to require it.
    # We will just remove the users from the organisation, but events' organisation field will be left as is or will be dropped by earlier migrations anyway.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0031_event_organisation"),
        ("organisations", "0002_create_default_organisation"),
        ("users", "0017_user_organisations"),
    ]

    operations = [
        migrations.RunPython(populate_events_and_admins, reverse_populate),
    ]
