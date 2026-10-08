from django.db import migrations

from kukkuu.settings import BROWSER_TEST_AD_GROUP_NAME, BROWSER_TEST_GROUP_NAME

# Group names taken from production database on 2026-10-08
YEAR_TO_GROUP_NAME: dict[int, str] = {
    2020: "2020 HKO",
    2021: "2021 Teatterit",
    2022: "2022",
    2023: "2023",
    2024: "2024",
    2025: "2025",
    2026: "2026",
}

# Azure AD group UUIDs taken from production database on 2026-10-08
UUID_MAPPINGS: list[tuple[str, int]] = [
    # 2020
    ("2ed07388-a088-4712-9599-4d878c455f51", 2020),
    ("5383c537-37cd-42a7-aa51-3f6111eb4cbc", 2020),
    # 2021
    ("f876b8e9-f654-4d9a-b521-fe417c4c9fe6", 2021),
    ("2b6fcc86-7769-482c-9790-3003f33989a9", 2021),
    # 2022
    ("6db55620-18c2-4241-9679-6ff1af1a47de", 2022),
    ("2b43f76c-c3c2-4633-8fae-1e1707a0cd95", 2022),
    # 2023
    ("8dc71950-85a2-404d-b877-8e870461a14d", 2023),
    ("a895ff48-55b2-4434-b252-0bf1bb3fdde8", 2023),
    # 2024
    ("86549c6a-728b-4dca-9db1-65cee683e69b", 2024),
    ("8113df32-fbc0-4624-aafe-42cb3afd0c6d", 2024),
    # 2025
    ("95805a3d-f146-4ecd-b30a-e67a65cf6f3f", 2025),
    # 2026
    ("35a819bb-5792-4542-8805-c1b251210bc7", 2026),
]

MAPPINGS: list[dict[str, str]] = [
    *(
        {
            "ad_group_name": f"az_kuva_asgd_u_kuku{year}",
            "ad_group_display_name": f"az_kuva_asgd_u_KUKU{year}",
            "group_name": YEAR_TO_GROUP_NAME[year],
        }
        for year in range(2020, 2027)
    ),
    *(
        {
            "ad_group_name": f"sg_kuva_kuku{year}",
            "ad_group_display_name": f"sg_KUVA_KUKU{year}",
            "group_name": YEAR_TO_GROUP_NAME[year],
        }
        for year in range(2020, 2025)
    ),
    *(
        {
            "ad_group_name": uuid,
            "ad_group_display_name": uuid,
            "group_name": YEAR_TO_GROUP_NAME[year],
        }
        for uuid, year in UUID_MAPPINGS
    ),
    {
        "ad_group_name": BROWSER_TEST_AD_GROUP_NAME,
        "ad_group_display_name": BROWSER_TEST_AD_GROUP_NAME,
        "group_name": BROWSER_TEST_GROUP_NAME,
    },
]


def clear_ad_group_mappings(apps, schema_editor):
    """Empty all ADGroupMapping records except the kukkuu_browser_test mapping."""
    ADGroupMapping = apps.get_model("helusers", "ADGroupMapping")
    ADGroupMapping.objects.exclude(
        ad_group__name__iexact=BROWSER_TEST_AD_GROUP_NAME
    ).delete()


def restore_ad_group_mappings(apps, schema_editor):
    """Restore default ADGroupMapping records for years 2020-2026 and browser tests.

    NOTE: The mapping might have been a bit different in different environments, because
    eventhough the AD-groups are quite static since they come from Azure,
    the group names are dynamic.
    """
    Group = apps.get_model("auth", "Group")
    ADGroup = apps.get_model("helusers", "ADGroup")
    ADGroupMapping = apps.get_model("helusers", "ADGroupMapping")

    for mapping in MAPPINGS:
        group, _ = Group.objects.get_or_create(name=mapping["group_name"])
        ad_group, _ = ADGroup.objects.get_or_create(
            name=mapping["ad_group_name"].lower(),
            defaults={"display_name": mapping["ad_group_display_name"]},
        )
        if ad_group.display_name != mapping["ad_group_display_name"]:
            ad_group.display_name = mapping["ad_group_display_name"]
            ad_group.save()
        ADGroupMapping.objects.get_or_create(group=group, ad_group=ad_group)


class Migration(migrations.Migration):
    """Empty AD-group mappings except the browser test mapping.

    This data migration is done because the event organizers are no longer
    ADFS users, but basic Helsinki-profile users that are managed by the
    product owner and other users with Django admin interface privileges.
    """

    dependencies = [
        ("users", "0016_user_last_api_use"),
    ]

    operations = [
        migrations.RunPython(
            clear_ad_group_mappings,
            restore_ad_group_mappings,
        ),
    ]
