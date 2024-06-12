from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class KukkuuMailerConfig(AppConfig):
    name = "kukkuu_mailer"
    verbose_name = _("Kukkuu mailer")
