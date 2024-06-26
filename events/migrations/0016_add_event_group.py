# Generated by Django 2.2.13 on 2020-11-17 09:43

import django.db.models.deletion
import parler.fields
import parler.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0003_upgrade_to_parler_2"),
        ("events", "0015_add_enrolment_reminder_sent_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventGroup",
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
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated_at"),
                ),
                (
                    "image",
                    models.ImageField(blank=True, upload_to="", verbose_name="image"),
                ),
                (
                    "published_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="published at"
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_groups",
                        to="projects.Project",
                        verbose_name="project",
                    ),
                ),
            ],
            options={
                "verbose_name": "event group",
                "verbose_name_plural": "event groups",
                "ordering": ("id",),
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.AlterField(
            model_name="event",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="events",
                to="projects.Project",
                verbose_name="project",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="event_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="events",
                to="events.EventGroup",
                verbose_name="event group",
            ),
        ),
        migrations.CreateModel(
            name="EventGroupTranslation",
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
                    "language_code",
                    models.CharField(
                        db_index=True, max_length=15, verbose_name="Language"
                    ),
                ),
                (
                    "name",
                    models.CharField(blank=True, max_length=255, verbose_name="name"),
                ),
                (
                    "short_description",
                    models.TextField(blank=True, verbose_name="short description"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
                ),
                (
                    "image_alt_text",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="image alt text"
                    ),
                ),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="events.EventGroup",
                    ),
                ),
            ],
            options={
                "verbose_name": "event group Translation",
                "db_table": "events_eventgroup_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "unique_together": {("language_code", "master")},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
