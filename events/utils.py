from collections.abc import Iterable
from datetime import datetime
from typing import List, Optional

from django.conf import settings
from django.utils import timezone
from django_ilmoitin.utils import send_notification
from parler.utils.context import switch_language

from common.utils import get_global_id


def send_event_notifications_to_guardians(
    event, notification_type, children, attachments: Optional[List] = None, **kwargs
):
    if not isinstance(children, Iterable):
        children = [children]

    for child in children:
        for guardian in child.guardians.all():
            with switch_language(event, guardian.language):
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
                    context["occurrence_enrol_url"] = get_occurrence_enrol_ui_url(
                        occurrence, child, guardian.language
                    )

                send_notification(
                    guardian.email,
                    notification_type,
                    context=context,
                    language=guardian.language,
                    attachments=attachments,
                )


def send_event_group_notifications_to_guardians(
    event_group, notification_type, children, **kwargs
):
    if not isinstance(children, Iterable):
        children = [children]

    for child in children:
        for guardian in child.guardians.all():
            with switch_language(event_group, guardian.language):
                context = {
                    "event_group": event_group,
                    "child": child,
                    "guardian": guardian,
                    "event_group_url": get_event_group_ui_url(
                        event_group, child, guardian.language
                    ),
                    "localtime": timezone.template_localtime,
                    "get_global_id": get_global_id,
                    "events": [
                        {
                            "obj": event,
                            "event_url": get_event_ui_url(
                                event, child, guardian.language
                            ),
                        }
                        for event in event_group.events.language(guardian.language)
                    ],
                    **kwargs,
                }

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


def get_event_group_ui_url(event_group, child, language):
    return "{}/{}/profile/child/{}/event-group/{}".format(
        settings.KUKKUU_UI_BASE_URL,
        language,
        get_global_id(child),
        get_global_id(event_group),
    )


def get_occurrence_ui_url(occurrence, child, language):
    return "{}/{}/profile/child/{}/occurrence/{}".format(
        settings.KUKKUU_UI_BASE_URL,
        language,
        get_global_id(child),
        get_global_id(occurrence),
    )


def get_occurrence_enrol_ui_url(occurrence, child, language):
    return "{}/{}/profile/child/{}/event/{}/occurrence/{}/enrol".format(
        settings.KUKKUU_UI_BASE_URL,
        language,
        get_global_id(child),
        get_global_id(occurrence.event),
        get_global_id(occurrence),
    )
