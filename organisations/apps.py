from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


def create_default_system_organisation(sender, **kwargs):
    from django.conf import settings

    from organisations.models import Organisation

    default_name = getattr(
        settings, "KUKKUU_DEFAULT_ORGANISATION_NAME", "Kukkuu system"
    )
    Organisation.objects.get_or_create(name=default_name)


class OrganisationsConfig(AppConfig):
    name = "organisations"
    verbose_name = _("Organisations")

    def ready(self):
        post_migrate.connect(create_default_system_organisation, sender=self)
