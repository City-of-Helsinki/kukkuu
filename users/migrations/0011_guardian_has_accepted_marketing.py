# Generated by Django 3.2.11 on 2024-03-19 14:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0010_alter_guardian_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="guardian",
            name="has_accepted_marketing",
            field=models.BooleanField(default=False, verbose_name="accepts marketing"),
        ),
    ]