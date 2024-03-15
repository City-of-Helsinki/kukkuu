# Generated by Django 2.2.13 on 2020-09-22 05:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("children", "0006_add_languages_spoken_at_home"),
        ("events", "0014_add_occurrence_capacity_override"),
    ]

    operations = [
        migrations.CreateModel(
            name="FreeSpotNotificationSubscription",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "child",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="free_spot_notification_subscriptions",
                        to="children.Child",
                        verbose_name="child",
                    ),
                ),
                (
                    "occurrence",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="free_spot_notification_subscriptions",
                        to="events.Occurrence",
                        verbose_name="occurrence",
                    ),
                ),
            ],
            options={
                "verbose_name": "free spot notification subscription",
                "verbose_name_plural": "free spot notification subscriptions",
                "ordering": ("id",),
            },
        ),
        migrations.AddConstraint(
            model_name="freespotnotificationsubscription",
            constraint=models.UniqueConstraint(
                fields=("child", "occurrence"), name="unique_free_spot_child_occurrence"
            ),
        ),
    ]
