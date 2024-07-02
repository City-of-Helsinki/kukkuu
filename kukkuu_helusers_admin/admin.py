from django.contrib import admin
from helusers.admin import ADGroupMappingAdmin
from helusers.models import ADGroup, ADGroupMapping


class KukkuuADGroupAdmin(admin.ModelAdmin):
    model = ADGroup
    search_fields = ("name",)


class KukkuuADGroupMappingAdmin(ADGroupMappingAdmin):
    """Override the ADGroupMappingAdmin provided by helusers."""

    search_fields = ("group__name", "ad_group__name", "ad_group__display_name")
    autocomplete_fields = ("group", "ad_group")


# Unregister the ADGroup admin provided by the `helusers`.
admin.site.unregister(ADGroup)
# Unregister the ADGroupMapping admin provided by the `helusers`.
admin.site.unregister(ADGroupMapping)

# Register a new admin for the ADGroupMapping.
admin.site.register(ADGroup, KukkuuADGroupAdmin)
# Register a new admin for the ADGroupMapping.
admin.site.register(ADGroupMapping, KukkuuADGroupMappingAdmin)
