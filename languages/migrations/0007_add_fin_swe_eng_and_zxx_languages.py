from django.db import migrations

# For "fin", "swe" and "eng": English names are from pycountry and Finnish and
# Swedish names from Unicode CLDR. The code "zxx" (No linguistic content) is used to
# mean "Speechless" and its translations were approved by the product owner.
LANGUAGE_NAMES = {
    "fin": {"en": "Finnish", "fi": "suomi", "sv": "finska"},
    "swe": {"en": "Swedish", "fi": "ruotsi", "sv": "svenska"},
    "eng": {"en": "English", "fi": "englanti", "sv": "engelska"},
    "zxx": {"en": "Speechless", "fi": "Sanaton", "sv": "Ordlös"},
}


def upsert_languages(apps, schema_editor):
    """
    Make sure "fin" (Finnish), "swe" (Swedish), "eng" (English) and "zxx"
    (Speechless) exist with the names from LANGUAGE_NAMES.
    """
    Language = apps.get_model("languages", "Language")
    LanguageTranslation = apps.get_model("languages", "LanguageTranslation")

    for alpha_3_code, names in LANGUAGE_NAMES.items():
        language, _ = Language.objects.get_or_create(alpha_3_code=alpha_3_code)
        for language_code, name in names.items():
            LanguageTranslation.objects.update_or_create(
                master=language, language_code=language_code, defaults={"name": name}
            )


class Migration(migrations.Migration):
    dependencies = [
        ("languages", "0006_update_alpha_3_code_help_text"),
    ]

    operations = [
        migrations.RunPython(upsert_languages, migrations.RunPython.noop),
    ]
