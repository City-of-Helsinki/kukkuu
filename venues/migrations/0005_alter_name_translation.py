# Generated by Django 2.2.10 on 2020-03-17 08:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("venues", "0004_venuetranslation_wc_and_facilities"),
    ]

    operations = [
        migrations.AlterField(
            model_name="venuetranslation",
            name="name",
            field=models.CharField(blank=True, max_length=255, verbose_name="name"),
        ),
    ]
