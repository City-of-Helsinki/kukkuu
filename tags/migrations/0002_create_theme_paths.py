from django.db import migrations

THEME_PATHS = [
    {
        "slug": "rhythm",
        "sort_order": 1,
        "translations": {
            "fi": {
                "name": "Rytmi",
                "description": "Rytmi-teemapolku koostuu musiikista ja tanssista.",
            },
            "sv": {
                "name": "Rytm",
                "description": 'Temavägen "Rytm" består av musik och dans.',
            },
            "en": {
                "name": "Rhythm",
                "description": 'Theme path "Rhythm" consists of music and dance.',
            },
        },
    },
    {
        "slug": "story",
        "sort_order": 2,
        "translations": {
            "fi": {
                "name": "Tarina",
                "description": "Tarina-teemapolku tarjoaa teatteria ja sirkusta.",
            },
            "sv": {
                "name": "Berättelse",
                "description": 'Temavägen "Berättelse" erbjuder teater och cirkus.',
            },
            "en": {
                "name": "Story",
                "description": 'Theme path "Story" features theater and circus.',
            },
        },
    },
    {
        "slug": "trace",
        "sort_order": 3,
        "translations": {
            "fi": {
                "name": "Jälki",
                "description": "Jälki-teemapolku sisältää visuaalisia taiteita, kulttuuriperintöä ja sanataidetta.",
            },
            "sv": {
                "name": "Spår",
                "description": 'Temavägen "Spår" omfattar bildkonst, kulturarv och litteratur.',
            },
            "en": {
                "name": "Trace",
                "description": 'Theme path "Trace" includes visual arts, cultural heritage, and literary arts.',
            },
        },
    },
]


def create_theme_paths(apps, schema_editor):
    ThemePath = apps.get_model("tags", "ThemePath")
    ThemePathTranslation = apps.get_model("tags", "ThemePathTranslation")

    for theme_path in THEME_PATHS:
        instance = ThemePath.objects.create(
            slug=theme_path["slug"], sort_order=theme_path["sort_order"]
        )
        for language_code, fields in theme_path["translations"].items():
            ThemePathTranslation.objects.create(
                master=instance, language_code=language_code, **fields
            )


def delete_theme_paths(apps, schema_editor):
    ThemePath = apps.get_model("tags", "ThemePath")
    ThemePath.objects.filter(slug__in=[tp["slug"] for tp in THEME_PATHS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("tags", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_theme_paths, delete_theme_paths),
    ]
