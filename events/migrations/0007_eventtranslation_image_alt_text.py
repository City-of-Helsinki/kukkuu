# Generated by Django 2.2.10 on 2020-03-16 08:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0006_add_enrolment_m2m_relationship"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventtranslation",
            name="image_alt_text",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="image alt text"
            ),
        ),
    ]
