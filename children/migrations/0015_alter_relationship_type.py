from django.db import migrations, models


def replace_null_relationship_types(apps, schema_editor):
    relationship = apps.get_model("children", "Relationship")
    relationship.objects.filter(type__isnull=True).update(type="")


class Migration(migrations.Migration):
    dependencies = [
        ("children", "0014_add_child_notes"),
    ]

    operations = [
        migrations.RunPython(
            replace_null_relationship_types,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="relationship",
            name="type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("parent", "Parent"),
                    ("other_guardian", "Other guardian"),
                    ("other_relation", "Other relation"),
                    ("advocate", "Advocate"),
                ],
                default="",
                max_length=64,
                verbose_name="type",
            ),
        ),
    ]
