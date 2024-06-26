# Generated by Django 3.2.11 on 2024-03-18 11:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("verification_tokens", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="verificationtoken",
            name="verification_type",
            field=models.CharField(
                choices=[
                    ("EMAIL_VERIFICATION", "Email verification"),
                    ("SUBSCRIPTIONS_AUTH", "Subscriptions management authorization"),
                ],
                max_length=64,
                verbose_name="verification type",
            ),
        ),
    ]
