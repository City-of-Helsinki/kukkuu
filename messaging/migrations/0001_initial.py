# Generated by Django 2.2.13 on 2020-10-19 08:41

import django.db.models.deletion
import parler.fields
import parler.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("projects", "0003_upgrade_to_parler_2"),
        ("events", "0015_add_enrolment_reminder_sent_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="Message",
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
                    "sent_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="sent at"),
                ),
                (
                    "recipient_count",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="recipient count"
                    ),
                ),
                (
                    "recipient_selection",
                    models.CharField(
                        choices=[
                            ("all", "All"),
                            ("invited", "Invited"),
                            ("enrolled", "Enrolled"),
                            ("attended", "Attended"),
                            (
                                "subscribed_to_free_spot_notification",
                                "Subscribed to free spot notification",
                            ),
                        ],
                        max_length=64,
                        verbose_name="recipient selection",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="events.Event",
                        verbose_name="event",
                    ),
                ),
                (
                    "occurrences",
                    models.ManyToManyField(
                        blank=True,
                        related_name="messages",
                        to="events.Occurrence",
                        verbose_name="occurrences",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="projects.Project",
                        verbose_name="project",
                    ),
                ),
            ],
            options={
                "verbose_name": "message",
                "verbose_name_plural": "messages",
                "ordering": ("id",),
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="MessageTranslation",
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
                ("subject", models.CharField(max_length=255, verbose_name="subject")),
                ("body_text", models.TextField(verbose_name="body plain text")),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="messaging.Message",
                    ),
                ),
            ],
            options={
                "verbose_name": "message Translation",
                "db_table": "messaging_message_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "unique_together": {("language_code", "master")},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
