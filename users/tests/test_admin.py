import pytest
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from users.admin import UserAdmin


@pytest.mark.django_db
def test_django_user_admin_fieldsets_structure():
    """
    Ensure upstream Django UserAdmin fieldsets maintain expected order and fields.
    If Django changes fieldset structure in an update, Kukkuu's UserAdmin.fieldsets
    slicing ([:2] and [3:]) may need to be adjusted.
    """
    assert len(DjangoUserAdmin.fieldsets) == 4, (
        "DjangoUserAdmin.fieldsets count changed. "
        "Review users.admin.UserAdmin.fieldsets slicing."
    )

    # Fieldset 0: Credentials
    assert DjangoUserAdmin.fieldsets[0][1]["fields"] == ("username", "password")

    # Fieldset 1: Personal info
    assert DjangoUserAdmin.fieldsets[1][1]["fields"] == (
        "first_name",
        "last_name",
        "email",
    )

    # Fieldset 2: Permissions (the overridden fieldset)
    expected_permission_fields = {
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
        "user_permissions",
    }
    assert (
        set(DjangoUserAdmin.fieldsets[2][1]["fields"]) == expected_permission_fields
    ), (
        "DjangoUserAdmin.fieldsets[2] fields changed. "
        "Ensure Kukkuu's custom fieldsets handle all permission fields."
    )

    # Fieldset 3: Important dates
    assert DjangoUserAdmin.fieldsets[3][1]["fields"] == ("last_login", "date_joined")


@pytest.mark.django_db
def test_kukkuu_user_admin_fieldsets_contain_all_fields():
    """
    Ensure Kukkuu's UserAdmin includes all standard Django User fields plus
    the custom UUID and organisations fields, without accidentally omitting any.
    """
    django_fields = {
        field for _, d in DjangoUserAdmin.fieldsets for field in d["fields"]
    }
    kukkuu_fields = {field for _, d in UserAdmin.fieldsets for field in d["fields"]}

    # All standard fields must be preserved
    missing_fields = django_fields - kukkuu_fields
    assert not missing_fields, (
        f"UserAdmin is missing fields from DjangoUserAdmin: {missing_fields}"
    )

    # Only uuid and organisations should be added beyond Django's default fields
    added_fields = kukkuu_fields - django_fields
    assert added_fields == {"uuid", "organisations"}


@pytest.mark.django_db
def test_kukkuu_user_admin_fieldsets_permissions_override():
    """
    Verify that fieldset 2 (Permissions) is replaced by custom fieldsets:
    - UUID
    - Organisations
    - Groups
    - User's global permissions (collapsed with warning description)
    """
    fieldset_titles = [title for title, _ in UserAdmin.fieldsets]
    assert "UUID" in fieldset_titles
    assert "Organisations" in fieldset_titles
    assert "Groups" in fieldset_titles
    assert "User's global permissions" in fieldset_titles

    # Global permissions fieldset should have warning description and collapse class
    global_perms_fieldset = next(
        d for title, d in UserAdmin.fieldsets if title == "User's global permissions"
    )
    assert "collapse" in global_perms_fieldset.get("classes", ())
    assert "description" in global_perms_fieldset
    assert "Warning: Permissions assigned here are GLOBAL" in str(
        global_perms_fieldset["description"]
    )
