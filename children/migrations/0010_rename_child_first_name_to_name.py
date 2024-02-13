# Generated by Django 3.2.11 on 2024-01-19 11:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("children", "0009_remove_child_lastname"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="child",
            options={
                "ordering": ["birthdate", "name"],
                "verbose_name": "child",
                "verbose_name_plural": "children",
            },
        ),
        migrations.RenameField(
            model_name="child",
            old_name="first_name",
            new_name="name",
        ),
        migrations.AlterField(
            model_name="child",
            name="name",
            field=models.CharField(blank=True, max_length=64, verbose_name="name"),
        ),
    ]