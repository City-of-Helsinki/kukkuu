from django.db import migrations

# In priority order for the reverse migration
ALPHA_3_CODES_BY_LOCALE = {"fi": "fin", "sv": "swe", "en": "eng"}


def copy_occurrence_language_to_languages(apps, schema_editor):
    """
    Give each occurrence the language row matching its occurrence_language code.
    """
    Occurrence = apps.get_model("events", "Occurrence")
    OccurrenceLanguage = apps.get_model("events", "OccurrenceLanguage")
    Language = apps.get_model("languages", "Language")

    language_ids = {
        locale: Language.objects.get(alpha_3_code=alpha_3_code).pk
        for locale, alpha_3_code in ALPHA_3_CODES_BY_LOCALE.items()
    }
    OccurrenceLanguage.objects.bulk_create(
        OccurrenceLanguage(occurrence_id=pk, language_id=language_ids[locale])
        for pk, locale in Occurrence.objects.values_list("pk", "occurrence_language")
    )


def copy_languages_to_occurrence_language(apps, schema_editor):
    """
    Best effort: set occurrence_language to the highest priority one of fi, sv and
    en that matches a language of the occurrence. Occurrences with none of those
    languages keep the field's default.
    """
    Occurrence = apps.get_model("events", "Occurrence")

    for locale, alpha_3_code in reversed(ALPHA_3_CODES_BY_LOCALE.items()):
        Occurrence.objects.filter(languages__alpha_3_code=alpha_3_code).update(
            occurrence_language=locale
        )


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0039_occurrence_languages"),
    ]

    operations = [
        migrations.RunPython(
            copy_occurrence_language_to_languages,
            copy_languages_to_occurrence_language,
        ),
    ]
