import base64
from typing import Tuple, TYPE_CHECKING

from django.conf import settings

from common.qrcode_service import create_qrcode, MIME_TYPES, QRCodeFileFormatEnum
from events.consts import NotificationType
from events.utils import send_event_notifications_to_guardians

if TYPE_CHECKING:
    from events.models import Enrolment

QRCODE_ATTACHMENT_FILE_FORMAT = QRCodeFileFormatEnum.PNG


def _get_ticket_filename(enrolment: "Enrolment", file_format: QRCodeFileFormatEnum):
    date_string = str(enrolment.occurrence.time.date())
    return f"KuKu-ticket-{date_string}-{enrolment.reference_id}.{file_format.value}"


def _decode_ticket_qrcode(ticket_qrcode: bytes, file_format: QRCodeFileFormatEnum.PNG):
    if file_format == QRCodeFileFormatEnum.PNG:
        return base64.b64encode(ticket_qrcode).decode()
    return ticket_qrcode.decode()


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
        _decode_ticket_qrcode(ticket_qrcode, file_format),  # content (decoded)
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
