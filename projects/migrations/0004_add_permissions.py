# Generated by Django 2.2.13 on 2020-12-23 10:14

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0003_upgrade_to_parler_2"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="project",
            options={
                "ordering": ["year"],
                "permissions": (
                    ("admin", "Base admin permission"),
                    ("publish", "Can publish"),
                ),
                "verbose_name": "project",
                "verbose_name_plural": "projects",
            },
        ),
        migrations.RemoveField(
            model_name="project",
            name="users",
        ),
    ]
