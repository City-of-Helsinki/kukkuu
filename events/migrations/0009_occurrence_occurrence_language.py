# Generated by Django 2.2.10 on 2020-03-26 12:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0008_alter_name_translation"),
    ]

    operations = [
        migrations.AddField(
            model_name="occurrence",
            name="occurrence_language",
            field=models.CharField(
                choices=[("fi", "Finnish"), ("en", "English"), ("sv", "Swedish")],
                default="fi",
                max_length=10,
                verbose_name="occurrence language",
            ),
        ),
    ]
