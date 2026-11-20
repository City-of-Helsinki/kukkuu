from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING, Optional, Tuple

from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone
from django_ilmoitin.utils import send_notification
from parler.utils.context import switch_language

from common.qrcode_service import MIME_TYPES, QRCodeFileFormatEnum, create_qrcode
from common.utils import get_global_id
from events.consts import NotificationType
from events.utils import (
    get_event_group_ui_url,
    get_event_ui_url,
    get_occurrence_enrol_ui_url,
    get_occurrence_ui_url,
)
from users.utils import get_communication_unsubscribe_ui_url

if TYPE_CHECKING:
    from children.models import Child
    from events.models import Enrolment, Event, EventGroup

logger = logging.getLogger(__name__)

QRCODE_ATTACHMENT_FILE_FORMAT = QRCodeFileFormatEnum.PNG


def send_event_notifications_to_guardians(
    event: "Event",
    notification_type: str,
    children: Child | QuerySet | list[Child],
    attachments: Optional[list] = None,
    **kwargs,
):
    """
    Send an event notification to all guardians of the given children who have
    accepted communication for the notification type.

    Contexts are collected per guardian email address before dispatching so that
    context errors do not cause partial duplicate mailings.
    """
    if not isinstance(children, Iterable):
        children = [children]

    context_for_address = {}

    for child in children:
        for guardian in child.guardians.has_accepted_communication_for_notification(
            notification_type
        ):
            with switch_language(event, guardian.language):
                context = {
                    "event": event,
                    "child": child,
                    "guardian": guardian,
                    "event_url": get_event_ui_url(event, child, guardian.language),
                    "localtime": timezone.template_localtime,
                    "get_global_id": get_global_id,
                    "is_sending_email": True,
                    "unsubscribe_url": get_communication_unsubscribe_ui_url(
                        guardian, guardian.language
                    ),
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
    notification_type: str,
    children: Child | QuerySet | list[Child],
    **kwargs,
):
    """
    Send an event group notification to all guardians of the given children who
    have accepted communication for the notification type.

    Renders the notification in each guardian's preferred language with the
    event group, its localized events, and email-specific context variables.
    """
    if not isinstance(children, Iterable):
        children = [children]

    for child in children:
        for guardian in child.guardians.has_accepted_communication_for_notification(
            notification_type
        ):
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
                            "registration_opens_at": event.registration_opens_at,
                        }
                        for event in event_group.events.language(guardian.language)
                    ],
                    "is_sending_email": True,
                    "unsubscribe_url": get_communication_unsubscribe_ui_url(
                        guardian, guardian.language
                    ),
                    **kwargs,
                }

                send_notification(
                    guardian.email,
                    notification_type,
                    context=context,
                    language=guardian.language,
                )


def _get_ticket_filename(enrolment: "Enrolment", file_format: QRCodeFileFormatEnum):
    date_string = str(enrolment.occurrence.time.date())
    return f"KuKu-ticket-{date_string}-{enrolment.reference_id}.{file_format.value}"


def create_ticket_as_attachment(
    enrolment: "Enrolment", file_format: QRCodeFileFormatEnum
) -> Tuple[str, str, str]:
    ticket_qrcode_content = settings.KUKKUU_TICKET_VERIFICATION_URL.format(
        reference_id=enrolment.reference_id
    )
    ticket_qrcode = create_qrcode(
        ticket_qrcode_content,
        file_format,
    )
    return (
        _get_ticket_filename(enrolment, file_format),  # file name
        ticket_qrcode,  # content (encoded)
        MIME_TYPES[file_format.value],  # MIME-type
    )


def send_enrolment_creation_notification(enrolment: "Enrolment"):
    attachments = []
    if settings.KUKKUU_TICKET_VERIFICATION_URL:
        ticket_qrcode = create_ticket_as_attachment(
            enrolment, QRCODE_ATTACHMENT_FILE_FORMAT
        )
        attachments.append(ticket_qrcode)
    send_event_notifications_to_guardians(
        enrolment.occurrence.event,
        NotificationType.OCCURRENCE_ENROLMENT,
        enrolment.child,
        occurrence=enrolment.occurrence,
        attachments=attachments,
    )


def send_event_reminder_notification(enrolment: "Enrolment"):
    attachments = []
    if settings.KUKKUU_TICKET_VERIFICATION_URL:
        ticket_qrcode = create_ticket_as_attachment(
            enrolment, QRCODE_ATTACHMENT_FILE_FORMAT
        )
        attachments.append(ticket_qrcode)
    send_event_notifications_to_guardians(
        enrolment.occurrence.event,
        NotificationType.OCCURRENCE_REMINDER,
        enrolment.child,
        occurrence=enrolment.occurrence,
        enrolment=enrolment,
        attachments=attachments,
    )
