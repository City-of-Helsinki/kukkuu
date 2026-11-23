from django.db import migrations, models


def set_flags_of_special_languages(apps, schema_editor):
    """
    "zxx" (Speechless) can't be a language spoken at home and "und" (Other) can't be
    an occurrence language.
    """
    Language = apps.get_model("languages", "Language")
    Language.objects.filter(alpha_3_code="zxx").update(can_be_spoken_at_home=False)
    Language.objects.filter(alpha_3_code="und").update(can_be_occurrence_language=False)


class Migration(migrations.Migration):
    dependencies = [
        ("languages", "0007_add_fin_swe_eng_and_zxx_languages"),
    ]

    operations = [
        migrations.AddField(
            model_name="language",
            name="can_be_occurrence_language",
            field=models.BooleanField(
                default=True,
                help_text="Whether this language can be chosen as an occurrence language and be used for filtering occurrences.",
                verbose_name="can be occurrence language",
            ),
        ),
        migrations.AddField(
            model_name="language",
            name="can_be_spoken_at_home",
            field=models.BooleanField(
                default=True,
                help_text="Whether this language can be chosen as a language spoken at home.",
                verbose_name="can be spoken at home",
            ),
        ),
        migrations.RunPython(set_flags_of_special_languages, migrations.RunPython.noop),
    ]
