from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EventsConfig(AppConfig):
    name = "events"
    verbose_name = _("events")

    def ready(self):
        import events.notifications  # noqa
        import events.signals  # noqa
