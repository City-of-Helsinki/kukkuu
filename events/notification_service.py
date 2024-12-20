from typing import TYPE_CHECKING, Tuple

from django.conf import settings

from common.qrcode_service import MIME_TYPES, QRCodeFileFormatEnum, create_qrcode
from events.consts import NotificationType
from events.utils import send_event_notifications_to_guardians

if TYPE_CHECKING:
    from events.models import Enrolment

QRCODE_ATTACHMENT_FILE_FORMAT = QRCodeFileFormatEnum.PNG


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
