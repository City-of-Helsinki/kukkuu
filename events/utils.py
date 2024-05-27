import logging
from collections.abc import Iterable
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, Union

from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone
from django_ilmoitin.utils import send_notification
from parler.utils.context import switch_language

from common.utils import get_global_id
from users.utils import get_communication_unsubscribe_ui_url

if TYPE_CHECKING:
    from children.models import Child
    from events.consts import NotificationType
    from events.models import Event, EventGroup

logger = logging.getLogger(__name__)


def send_event_notifications_to_guardians(
    event: "Event",
    notification_type: "NotificationType",
    children: Union[QuerySet, List["Child"]],
    attachments: Optional[List] = None,
    **kwargs,
):
    if not isinstance(children, Iterable):
        children = [children]

    context_for_address = {}

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
                    "unsubscribe_url": get_communication_unsubscribe_ui_url(
                        guardian, guardian.language
                    ),
                    "is_obsolete": child.is_obsolete,
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
                context_for_address[guardian.email] = context

    emails = ",".join(context_for_address.keys())
    logger.debug(
        f"There are {len(emails)} total in the notification list. "
        f"Notification will be sent to these addresses: {emails}"
    )
    # NOTE: Instead of sending the notification in the previous loop,
    # lets first collect the mail contexts to a dictionary and
    # send the mails after all the contexts have been handled properly.
    # This way we can prevent flooding the recipients with the mails
    # when some of the contexts cannot be handled because of any reason.
    # For more details, see
    # 1. https://helsinkisolutionoffice.atlassian.net/browse/KK-984,
    # 2. https://helsinkisolutionoffice.atlassian.net/browse/PT-1414.
    for address, context in context_for_address.items():
        logger.debug(f"Sending event notification to {address}.")
        guardian = context["guardian"]
        send_notification(
            email=address,
            notification_type=notification_type,
            context=context,
            language=guardian.language,
            attachments=attachments,
        )


def send_event_group_notifications_to_guardians(
    event_group: "EventGroup",
    notification_type: "NotificationType",
    children: Union[QuerySet, List["Child"]],
    **kwargs,
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
                    "unsubscribe_url": get_communication_unsubscribe_ui_url(
                        guardian, guardian.language
                    ),
                    "is_obsolete": child.is_obsolete,
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
