# Generated by Django 2.2.13 on 2021-08-12 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0020_add_occurrence_ticket_system_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="capacity_per_occurrence",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="capacity per occurrence"
            ),
        ),
    ]
