from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


def create_default_system_organisation(sender, **kwargs):
    from organisations.models import Organisation

    if Organisation.objects.filter(is_system=True).exists():
        return

    default_name = getattr(settings, "KUKKUU_DEFAULT_ORGANISATION_NAME", None)
    if not default_name:
        raise ImproperlyConfigured(
            "KUKKUU_DEFAULT_ORGANISATION_NAME setting must be set."
        )
    org = Organisation.objects.filter(name=default_name).first()
    if org:
        if not org.is_system:
            org.is_system = True
            org.save(update_fields=["is_system"])
    else:
        Organisation.objects.create(name=default_name, is_system=True)


class OrganisationsConfig(AppConfig):
    name = "organisations"
    verbose_name = _("Organisations")

    def ready(self):
        post_migrate.connect(create_default_system_organisation, sender=self)
