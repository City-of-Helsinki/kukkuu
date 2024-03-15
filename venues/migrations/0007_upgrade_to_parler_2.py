# Generated by Django 2.2.13 on 2020-08-24 13:15

import django.db.models.deletion
import parler.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("venues", "0006_venue_project"),
    ]

    operations = [
        migrations.AlterField(
            model_name="venuetranslation",
            name="master",
            field=parler.fields.TranslationsForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="translations",
                to="venues.Venue",
            ),
        ),
    ]
