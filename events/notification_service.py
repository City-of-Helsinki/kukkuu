from typing import TYPE_CHECKING

from django.conf import settings

from common.qrcode_service import create_qrcode
from events.consts import NotificationType
from events.utils import send_event_notifications_to_guardians

if TYPE_CHECKING:
    from events.models import Enrolment


def _get_ticket_filename(enrolment: "Enrolment"):
    date_string = str(enrolment.occurrence.time.date())
    return f"KuKu-ticket-{date_string}-{enrolment.reference_id}.svg"


def send_enrolment_creation_notification(enrolment: "Enrolment"):
    attachments = []
    if settings.KUKKUU_TICKET_VERIFICATION_URL:
        ticket_qrcode_content = settings.KUKKUU_TICKET_VERIFICATION_URL.format(
            reference_id=enrolment.reference_id
        )
        ticket_qrcode = create_qrcode(
            ticket_qrcode_content,
            "svg",
        )
        attachments.append(
            (
                _get_ticket_filename(enrolment),  # file name
                ticket_qrcode.decode(),  # content (decoded)
                "image/svg+xml",  # MIME-type
            )
        )
    send_event_notifications_to_guardians(
        enrolment.occurrence.event,
        NotificationType.OCCURRENCE_ENROLMENT,
        enrolment.child,
        occurrence=enrolment.occurrence,
        attachments=attachments,
    )
