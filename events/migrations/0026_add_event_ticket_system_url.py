# Generated by Django 3.2.11 on 2022-09-30 11:43

from django.db import migrations, models


def populate_ticket_system_url(apps, schema_editor):
    # Populate Event ticket_system_url with the URL of the first occurrence just to get
    # some values to test and local envs more conveniently.
    Event = apps.get_model("events", "Event")
    for event in Event.objects.exclude(ticket_system="internal"):
        if (
            occurrence_with_ticket_system_url := event.occurrences.exclude(
                ticket_system_url=""
            )
            .order_by("id")
            .first()
        ):
            event.ticket_system_url = (
                occurrence_with_ticket_system_url.ticket_system_url
            )
            event.save(update_fields=("ticket_system_url",))


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0025_alter_enrolment_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="ticket_system_url",
            field=models.URLField(blank=True, verbose_name="ticket system URL"),
        ),
        migrations.RunPython(populate_ticket_system_url, migrations.RunPython.noop),
    ]
