import importlib

import pytest
from django.apps import apps
from django.conf import settings
from django.db import migrations

from organisations.models import Organisation

migration_module = importlib.import_module(
    "organisations.migrations.0002_create_default_organisation"
)
create_default_organisation = migration_module.create_default_organisation
Migration = migration_module.Migration


@pytest.mark.django_db
def test_create_default_organisation_forward_and_reverse_noop():
    default_name = getattr(
        settings, "KUKKUU_DEFAULT_ORGANISATION_NAME", "Hekla (system)"
    )
    # Ensure organisation exists
    create_default_organisation(apps, None)
    assert Organisation.objects.filter(name=default_name).exists()

    # Verify that the reverse operation is migrations.RunPython.noop
    migration_instance = Migration("0002_create_default_organisation", "organisations")
    run_python_op = migration_instance.operations[0]
    assert run_python_op.reverse_code is migrations.RunPython.noop
