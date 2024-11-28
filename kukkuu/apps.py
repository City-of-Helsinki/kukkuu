from django.apps import AppConfig


class KukkuuProjectConfig(AppConfig):
    name = "kukkuu"

    def ready(self):
        from hel_django_auditlog_extra.utils import AuditLogConfigurationHelper

        AuditLogConfigurationHelper.raise_error_if_unconfigured_models()
