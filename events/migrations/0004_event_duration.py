# Generated by Django 2.2.9 on 2020-01-23 10:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0003_modify_events_and_occurrences_table"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="duration",
            field=models.DurationField(blank=True, null=True, verbose_name="duration"),
        ),
    ]
