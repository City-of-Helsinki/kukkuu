# Generated by Django 2.2.6 on 2019-11-24 20:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("children", "0003_change_relationship_point_to_guardian")]

    operations = [
        migrations.AddField(
            model_name="child",
            name="postal_code",
            field=models.CharField(
                max_length=5,
                verbose_name="postal code",
                validators=[
                    django.core.validators.RegexValidator(
                        code="invalid_postal_code",
                        message="Postal code must be 5 digits",
                        regex="^\\d{5}$",
                    )
                ],
            ),
        )
    ]
