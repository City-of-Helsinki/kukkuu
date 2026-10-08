from django.db import migrations, models


def set_registration_opens_at_to_published_at(apps, schema_editor):
    Event = apps.get_model("events", "Event")
    Event.objects.update(registration_opens_at=models.F("published_at"))


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0030_add_tixly_ticket_system"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="registration_opens_at",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="registration opens at"
            ),
        ),
        migrations.RunPython(
            set_registration_opens_at_to_published_at, migrations.RunPython.noop
        ),
    ]
