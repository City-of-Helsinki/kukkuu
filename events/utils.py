from collections import Iterable
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from django_ilmoitin.utils import send_notification

from common.utils import get_global_id


def send_event_notifications_to_guardians(event, notification_type, children, **kwargs):
    if not isinstance(children, Iterable):
        children = [children]

    for child in children:
        for guardian in child.guardians.all():
            context = {
                "event": event,
                "child": child,
                "guardian": guardian,
                "event_url": get_event_ui_url(event, child, guardian.language),
                "localtime": timezone.template_localtime,
                "get_global_id": get_global_id,
                **kwargs,
            }
            occurrence = kwargs.get("occurrence")
            if occurrence:
                context["occurrence_url"] = get_occurrence_ui_url(
                    occurrence, child, guardian.language
                )

            send_notification(
                guardian.email,
                notification_type,
                context=context,
                language=guardian.language,
            )


def convert_to_localtime_tz(value):
    dt = datetime.combine(datetime.now().date(), value)
    if timezone.is_naive(value):
        # Auto add local timezone to naive time
        return timezone.make_aware(dt).timetz()
    else:
        return timezone.localtime(dt).timetz()


def get_event_ui_url(event, child, language):
    return "{}/{}/profile/child/{}/event/{}".format(
        settings.KUKKUU_UI_BASE_URL,
        language,
        get_global_id(child),
        get_global_id(event),
    )


def get_occurrence_ui_url(occurrence, child, language):
    return "{}/{}/profile/child/{}/occurrence/{}".format(
        settings.KUKKUU_UI_BASE_URL,
        language,
        get_global_id(child),
        get_global_id(occurrence),
    )
