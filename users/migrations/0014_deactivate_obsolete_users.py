from django.db import migrations


def deactivate_obsolete_users(apps, schema_editor):
    """Deactivate all the users that are marked as obsolete.
    It marks all the users that are marked as obsolete
    as inactive.

    NOTE: The obsoleted state is originally set by a migration
    process when Tunnistamo was changed to a Keycloak service.
    After that migration, the users were marked as obsolete
    but left as active. Obsolete status was like a
    "safe deactivation".
    """
    User = apps.get_model("users", "User")
    User.objects.filter(is_obsolete=True).update(is_active=False)


def reactivate_obsolete_users(apps, schema_editor):
    """Reverse the deactivation of obsolete users.
    It marks all the users that are marked as obsolete
    as active again.

    NOTE: This might reactivate also some users
    that were explicitly deactivated by the admin.
    """
    User = apps.get_model("users", "User")
    User.objects.filter(is_obsolete=True).update(is_active=True)


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0013_replace_has_accepted_marketing_with_communication"),
    ]

    operations = [
        migrations.RunPython(
            deactivate_obsolete_users,
            reactivate_obsolete_users,
        ),
    ]
