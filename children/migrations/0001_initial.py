# Generated by Django 2.2.6 on 2019-10-10 13:35

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Child",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        primary_key=True,
                        serialize=False,
                        verbose_name="UUID",
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
                    "first_name",
                    models.CharField(max_length=64, verbose_name="first name"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=64, verbose_name="last name"),
                ),
                ("birthdate", models.DateField(verbose_name="birthdate")),
                (
                    "social_security_number_hash",
                    models.CharField(
                        editable=False,
                        max_length=255,
                        verbose_name="social security number hash",
                    ),
                ),
            ],
            options={"verbose_name": "child", "verbose_name_plural": "children"},
        ),
        migrations.CreateModel(
            name="Relationship",
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
                    "type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("parent", "Parent"),
                            ("other_guardian", "Other guardian"),
                            ("other_relation", "Other relation"),
                            ("advocate", "Advocate"),
                        ],
                        max_length=64,
                        null=True,
                        verbose_name="type",
                    ),
                ),
                (
                    "child",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="relationships",
                        to="children.Child",
                        verbose_name="child",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="relationships",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="user",
                    ),
                ),
            ],
            options={
                "verbose_name": "relationship",
                "verbose_name_plural": "relationships",
            },
        ),
        migrations.AddField(
            model_name="child",
            name="users",
            field=models.ManyToManyField(
                blank=True,
                related_name="children",
                through="children.Relationship",
                to=settings.AUTH_USER_MODEL,
                verbose_name="users",
            ),
        ),
    ]
