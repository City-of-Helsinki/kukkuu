# Generated by Django 3.2.11 on 2024-05-02 13:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0011_guardian_has_accepted_marketing"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_obsolete",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether the user account is obsoleted and cannot be anymore accessed, e.g. after an auth service change process (when the Tunnistamo is changed to a Keycloak service).",
                verbose_name="obsoleted",
            ),
        ),
    ]