# Generated by Django 2.2.13 on 2020-08-27 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0012_upgrade_to_parler_2"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="participants_per_invite",
            field=models.CharField(
                choices=[
                    ("child_and_guardian", "Child and guardian"),
                    ("child_and_1_or_2_guardians", "Child and 1-2 guardians"),
                    ("family", "Family"),
                ],
                max_length=255,
                verbose_name="participants per invite",
            ),
        ),
    ]