from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class KukkuuMailerAdminConfig(AppConfig):
    name = "kukkuu_mailer_admin"
    verbose_name = _("Kukkuu mailer admin")
