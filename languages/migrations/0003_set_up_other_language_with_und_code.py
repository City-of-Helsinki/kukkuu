from django.db import migrations

OTHER_LANGUAGE_ALPHA_3_CODE = "und"
OTHER_LANGUAGE_NAMES = {
    "fi": "Muu kieli",
    "sv": "Annat språk",
    "en": "Other language",
}


def set_up_other_language(apps, schema_editor):
    """
    Make sure there is exactly one "Other language" row, with the alpha-3 code
    "und" and the names from OTHER_LANGUAGE_NAMES, so that alpha_3_code can be made
    non-nullable.
    """
    Language = apps.get_model("languages", "Language")
    LanguageTranslation = apps.get_model("languages", "LanguageTranslation")

    null_code_ids = list(
        Language.objects.filter(alpha_3_code__isnull=True)
        .order_by("id")
        .values_list("id", flat=True)
    )
    if len(null_code_ids) > 1:
        raise RuntimeError(
            f"Found multiple languages with null alpha_3_code (ids: {null_code_ids}). "
            "Handle them manually (e.g. merge them into one or give them proper "
            "alpha_3_codes) before running this migration."
        )

    language_with_und_code = Language.objects.filter(
        alpha_3_code=OTHER_LANGUAGE_ALPHA_3_CODE
    ).first()

    if null_code_ids and language_with_und_code:
        raise RuntimeError(
            f"Found both a language with null alpha_3_code (id: {null_code_ids[0]}) "
            f'and a language with alpha_3_code "{OTHER_LANGUAGE_ALPHA_3_CODE}" '
            f"(id: {language_with_und_code.id}). Handle them manually before "
            "running this migration."
        )

    if null_code_ids:
        language = Language.objects.get(id=null_code_ids[0])
        language.alpha_3_code = OTHER_LANGUAGE_ALPHA_3_CODE
        language.save()
    elif language_with_und_code:
        language = language_with_und_code
    else:
        language = Language.objects.create(alpha_3_code=OTHER_LANGUAGE_ALPHA_3_CODE)

    for language_code, name in OTHER_LANGUAGE_NAMES.items():
        LanguageTranslation.objects.update_or_create(
            master=language, language_code=language_code, defaults={"name": name}
        )


def revert_other_language_code(apps, schema_editor):
    Language = apps.get_model("languages", "Language")
    Language.objects.filter(alpha_3_code=OTHER_LANGUAGE_ALPHA_3_CODE).update(
        alpha_3_code=None
    )


class Migration(migrations.Migration):
    dependencies = [
        ("languages", "0002_make_alpha_3_code_nullable"),
    ]

    operations = [
        migrations.RunPython(set_up_other_language, revert_other_language_code),
    ]
