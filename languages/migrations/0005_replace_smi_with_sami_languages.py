from django.db import migrations

# English names are from pycountry, Finnish and Swedish names from Unicode CLDR.
SAMI_LANGUAGE_NAMES = {
    "sme": {"en": "Northern Sami", "fi": "pohjoissaame", "sv": "nordsamiska"},
    "smn": {"en": "Inari Sami", "fi": "inarinsaame", "sv": "enaresamiska"},
    "sms": {"en": "Skolt Sami", "fi": "koltansaame", "sv": "skoltsamiska"},
}


def rename_smi_to_sme(apps, schema_editor):
    """
    Replace the ISO 639-5 code "smi" (Sami languages, a language family) with the
    ISO 639-3 code "sme" (Northern Sami) by renaming the row, so that its relations
    are kept.
    """
    Language = apps.get_model("languages", "Language")

    if (
        Language.objects.filter(alpha_3_code="smi").exists()
        and Language.objects.filter(alpha_3_code="sme").exists()
    ):
        raise RuntimeError(
            'Found both a language with alpha_3_code "smi" and a language with '
            'alpha_3_code "sme". Handle them manually (e.g. merge them into one) '
            "before running this migration."
        )

    Language.objects.filter(alpha_3_code="smi").update(alpha_3_code="sme")


def rename_sme_to_smi(apps, schema_editor):
    Language = apps.get_model("languages", "Language")
    Language.objects.filter(alpha_3_code="sme").update(alpha_3_code="smi")


def upsert_sme_smn_sms_languages(apps, schema_editor):
    """
    Make sure "sme" (Northern Sami), "smn" (Inari Sami) and "sms" (Skolt Sami) exist
    with the names from SAMI_LANGUAGE_NAMES.
    """
    Language = apps.get_model("languages", "Language")
    LanguageTranslation = apps.get_model("languages", "LanguageTranslation")

    for alpha_3_code, names in SAMI_LANGUAGE_NAMES.items():
        language, _ = Language.objects.get_or_create(alpha_3_code=alpha_3_code)
        for language_code, name in names.items():
            LanguageTranslation.objects.update_or_create(
                master=language, language_code=language_code, defaults={"name": name}
            )


class Migration(migrations.Migration):
    dependencies = [
        ("languages", "0004_make_alpha_3_code_non_nullable"),
    ]

    operations = [
        migrations.RunPython(rename_smi_to_sme, rename_sme_to_smi),
        migrations.RunPython(upsert_sme_smn_sms_languages, migrations.RunPython.noop),
    ]
