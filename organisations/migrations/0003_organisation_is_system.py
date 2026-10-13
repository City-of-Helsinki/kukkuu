import logging

from django.conf import settings
from django.db import migrations, models

logger = logging.getLogger(__name__)


def set_system_organisation(apps, schema_editor):
    Organisation = apps.get_model("organisations", "Organisation")
    if Organisation.objects.filter(is_system=True).exists():
        return

    default_name = getattr(
        settings, "KUKKUU_DEFAULT_ORGANISATION_NAME", "Hekla (system)"
    )
    org = Organisation.objects.filter(name=default_name).first()
    if not org:
        org = Organisation.objects.filter(name="Hekla (system)").first()
    if not org:
        org = Organisation.objects.first()

    if org:
        org.is_system = True
        org.save(update_fields=["is_system"])
        logger.info(f"Set is_system=True on organisation: {org.name}")
    else:
        Organisation.objects.create(name=default_name, is_system=True)
        logger.info(f"Created default system organisation: {default_name}")


class Migration(migrations.Migration):
    dependencies = [
        ("organisations", "0002_create_default_organisation"),
    ]

    operations = [
        migrations.AddField(
            model_name="organisation",
            name="is_system",
            field=models.BooleanField(default=False, verbose_name="is system"),
        ),
        migrations.RunPython(set_system_organisation, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="organisation",
            constraint=models.UniqueConstraint(
                condition=models.Q(is_system=True),
                fields=("is_system",),
                name="unique_system_organisation",
            ),
        ),
    ]
