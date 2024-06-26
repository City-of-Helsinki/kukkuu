# Generated by Django 2.2.6 on 2019-10-19 21:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_add_guardian"),
        ("children", "0002_remove_child_ssn"),
    ]

    operations = [
        migrations.RemoveField(model_name="child", name="users"),
        migrations.RemoveField(model_name="relationship", name="user"),
        migrations.AddField(
            model_name="child",
            name="guardians",
            field=models.ManyToManyField(
                blank=True,
                related_name="children",
                through="children.Relationship",
                to="users.Guardian",
                verbose_name="guardians",
            ),
        ),
        migrations.AddField(
            model_name="relationship",
            name="guardian",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="relationships",
                to="users.Guardian",
                verbose_name="guardian",
            ),
        ),
        migrations.AlterField(
            model_name="child",
            name="first_name",
            field=models.CharField(
                blank=True, max_length=64, verbose_name="first name"
            ),
        ),
        migrations.AlterField(
            model_name="child",
            name="last_name",
            field=models.CharField(blank=True, max_length=64, verbose_name="last name"),
        ),
    ]
