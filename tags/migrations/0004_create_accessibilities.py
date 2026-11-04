from django.db import migrations

ACCESSIBILITIES = [
    {
        "slug": "sensory_sensitivity",
        "sort_order": 1,
        "translations": {
            "fi": {
                "name": "Aistiherkkyys",
                "description": "Aistiherkkyys huomioitu",
            },
            "sv": {
                "name": "Sensorisk känslighet",
                "description": "Sensorisk känslighet beaktad",
            },
            "en": {
                "name": "Sensory sensitivity",
                "description": "Sensory sensitivity considered",
            },
        },
    },
    {
        "slug": "executive_function",
        "sort_order": 2,
        "translations": {
            "fi": {
                "name": "Toiminnanohjauksen tuki",
                "description": "Toiminnanohjauksen tuen tarve huomioitu",
            },
            "sv": {
                "name": "Stöd för exekutiva funktioner",
                "description": "Behovet av stöd för exekutiva funktioner har beaktats",
            },
            "en": {
                "name": "Executive function support",
                "description": "Need for executive function support considered",
            },
        },
    },
    {
        "slug": "vision",
        "sort_order": 3,
        "translations": {
            "fi": {
                "name": "Näkemisen tuki",
                "description": "Näkemisen tuen tarve huomioitu",
            },
            "sv": {
                "name": "Stöd för synen",
                "description": "Behov kopplade till synen beaktade",
            },
            "en": {
                "name": "Vision support",
                "description": "Need for vision support considered",
            },
        },
    },
    {
        "slug": "hearing",
        "sort_order": 4,
        "translations": {
            "fi": {
                "name": "Kuulemisen tuki",
                "description": "Kuulemisen tuen tarve huomioitu",
            },
            "sv": {
                "name": "Stöd för hörseln",
                "description": "Behov kopplade till hörseln beaktade",
            },
            "en": {
                "name": "Hearing support",
                "description": "Need for hearing support considered",
            },
        },
    },
    {
        "slug": "mobility",
        "sort_order": 5,
        "translations": {
            "fi": {
                "name": "Liikkumisrajoitteet",
                "description": "Liikkumisen tuen tarve huomioitu",
            },
            "sv": {
                "name": "Nedsatt rörlighet",
                "description": "Behov kopplade till nedsatt rörlighet beaktade",
            },
            "en": {
                "name": "Limited mobility",
                "description": "Need for limited mobility support considered",
            },
        },
    },
]


def create_accessibilities(apps, schema_editor):
    Accessibility = apps.get_model("tags", "Accessibility")
    AccessibilityTranslation = apps.get_model("tags", "AccessibilityTranslation")

    for accessibility in ACCESSIBILITIES:
        instance = Accessibility.objects.create(
            slug=accessibility["slug"], sort_order=accessibility["sort_order"]
        )
        for language_code, fields in accessibility["translations"].items():
            AccessibilityTranslation.objects.create(
                master=instance, language_code=language_code, **fields
            )


def delete_accessibilities(apps, schema_editor):
    Accessibility = apps.get_model("tags", "Accessibility")
    Accessibility.objects.filter(
        slug__in=[accessibility["slug"] for accessibility in ACCESSIBILITIES]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("tags", "0003_accessibility"),
    ]

    operations = [
        migrations.RunPython(create_accessibilities, delete_accessibilities),
    ]
