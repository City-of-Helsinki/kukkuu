# Generated by Django 3.2.11 on 2022-03-02 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("messaging", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="protocol",
            field=models.CharField(
                choices=[("email", "Email"), ("sms", "SMS")],
                default="email",
                max_length=16,
                verbose_name="notification type",
            ),
        ),
    ]
