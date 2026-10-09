import logging

from django.conf import settings
from django.db import migrations

logger = logging.getLogger(__name__)


def create_default_organisation(apps, schema_editor):
    Organisation = apps.get_model("organisations", "Organisation")
    default_name = getattr(
        settings, "KUKKUU_DEFAULT_ORGANISATION_NAME", "Kukkuu system"
    )
    org, created = Organisation.objects.get_or_create(name=default_name)
    if created:
        logger.info(f"Created default system organisation: {default_name}")


def remove_default_organisation(apps, schema_editor):
    Organisation = apps.get_model("organisations", "Organisation")
    default_name = getattr(
        settings, "KUKKUU_DEFAULT_ORGANISATION_NAME", "Kukkuu system"
    )
    Organisation.objects.filter(name=default_name).delete()
    logger.info(f"Removed default system organisation: {default_name}")


class Migration(migrations.Migration):
    dependencies = [
        ("organisations", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_organisation, remove_default_organisation),
    ]
