import pytest

from common.qrcode_service import create_qrcode, QRCodeFileFormatEnum
from kukkuu.service import get_hashid_service


@pytest.mark.parametrize(
    "file_format",
    [QRCodeFileFormatEnum.SVG, QRCodeFileFormatEnum.PNG],
)
def test_qrcode_creation(file_format, snapshot):
    hashids = get_hashid_service()
    url = "https://kukkuu-admin.test.kuva.hel.ninja/check-validity/{reference_id}"
    enrolment_reference_ids = [
        hashids.encode(1),
        hashids.encode(2),
        hashids.encode(999),
    ]
    for reference_id in enrolment_reference_ids:
        snapshot.assert_match(
            str(create_qrcode(url.format(reference_id=reference_id), file_format))
        )
