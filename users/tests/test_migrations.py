import importlib

import pytest
from django.apps import apps
from django.contrib.auth.models import Group
from helusers.models import ADGroup, ADGroupMapping

migration_module = importlib.import_module(
    "users.migrations.0017_clear_ad_group_mappings"
)
MAPPINGS = migration_module.MAPPINGS
clear_ad_group_mappings = migration_module.clear_ad_group_mappings
restore_ad_group_mappings = migration_module.restore_ad_group_mappings


@pytest.mark.django_db
def test_ad_group_mappings_migration_forward_and_reverse():
    # Setup initial state with custom mappings and browser test mapping
    test_group, _ = Group.objects.get_or_create(name="Browser test")
    browser_ad_group, _ = ADGroup.objects.get_or_create(
        name="kukkuu_browser_test",
        defaults={"display_name": "kukkuu_browser_test"},
    )
    ADGroupMapping.objects.get_or_create(
        group=test_group,
        ad_group=browser_ad_group,
    )

    other_group, _ = Group.objects.get_or_create(name="Other group")
    other_ad_group, _ = ADGroup.objects.get_or_create(
        name="other_ad_group",
        defaults={"display_name": "Other AD Group"},
    )
    ADGroupMapping.objects.get_or_create(
        group=other_group,
        ad_group=other_ad_group,
    )

    # 1. Forward migration: should empty everything except kukkuu_browser_test
    clear_ad_group_mappings(apps, None)

    assert ADGroupMapping.objects.count() == 1
    remaining_mapping = ADGroupMapping.objects.first()
    assert remaining_mapping.ad_group.name == "kukkuu_browser_test"
    assert remaining_mapping.group.name == "Browser test"

    # 2. Reverse migration: should restore all 15 mappings
    restore_ad_group_mappings(apps, None)

    assert ADGroupMapping.objects.count() == len(MAPPINGS)
    for mapping_data in MAPPINGS:
        mapping = ADGroupMapping.objects.filter(
            ad_group__name=mapping_data["ad_group_name"],
            group__name=mapping_data["group_name"],
        ).first()
        assert mapping is not None
        assert mapping.ad_group.display_name == mapping_data["ad_group_display_name"]

    # 3. Forward migration again: should empty everything except kukkuu_browser_test
    clear_ad_group_mappings(apps, None)

    assert ADGroupMapping.objects.count() == 1
    remaining_mapping = ADGroupMapping.objects.first()
    assert remaining_mapping.ad_group.name == "kukkuu_browser_test"
    assert remaining_mapping.group.name == "Browser test"
