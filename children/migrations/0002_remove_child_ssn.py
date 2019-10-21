# Generated by Django 2.2.6 on 2019-10-15 19:17
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("children", "0001_initial")]

    operations = [
        migrations.RenameField(model_name="child", old_name="uuid", new_name="id"),
        migrations.RemoveField(model_name="child", name="social_security_number_hash"),
        migrations.AlterField(
            model_name="child",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                primary_key=True,
                serialize=False,
                verbose_name="UUID",
            ),
        ),
    ]
