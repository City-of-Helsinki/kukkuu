from django.db import migrations
from django.core.management import call_command

def load_project_data(apps, schema_editor):
    call_command('load_project_data')

class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_add_messaging_permission'),
    ]

    operations = [
        migrations.RunPython(load_project_data),
    ]