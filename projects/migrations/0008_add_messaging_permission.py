# Generated by Django 4.2.14 on 2024-10-14 12:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_project_enrolment_limit'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'default_permissions': [], 'ordering': ['year'], 'permissions': (('admin', 'Base admin permission'), ('publish', 'Can publish events and event groups'), ('manage_event_groups', 'Can create, update and delete event groups'), ('can_send_to_all_in_project', 'Can send messages to all recipients in project')), 'verbose_name': 'project', 'verbose_name_plural': 'projects'},
        ),
    ]
