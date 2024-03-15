# Generated by Django 2.2.10 on 2020-06-10 09:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0010_event_project"),
    ]

    operations = [
        migrations.AddField(
            model_name="enrolment",
            name="attended",
            field=models.NullBooleanField(verbose_name="attended"),
        ),
        migrations.AddField(
            model_name="enrolment",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="updated_at"),
        ),
    ]
