# Generated by Django 3.2.11 on 2024-01-19 09:03

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("children", "0008_alter_relationship_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="child",
            options={
                "ordering": ["birthdate", "first_name"],
                "verbose_name": "child",
                "verbose_name_plural": "children",
            },
        ),
        migrations.RemoveField(
            model_name="child",
            name="last_name",
        ),
    ]
