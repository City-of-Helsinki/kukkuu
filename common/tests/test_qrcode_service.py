from io import BytesIO

import pytest
from PIL import Image

from common.qrcode_service import QRCodeFileFormatEnum, create_qrcode
from kukkuu.service import get_hashid_service


def _qrcode_snapshot_value(
    qrcode_bytes: bytes, file_format: QRCodeFileFormatEnum
) -> str:
    """Return a platform-independent representation of the generated QR code.

    PNG bytes are re-encoded by Pillow/zlib, whose compressed output can differ
    between platforms (e.g. macOS vs. Linux) even for identical pixel data, so
    comparing raw bytes is flaky across CI environments. Decoding the image and
    snapshotting the pixel data instead keeps the test deterministic.
    """
    if file_format is QRCodeFileFormatEnum.PNG:
        image = Image.open(BytesIO(qrcode_bytes))
        return str((image.mode, image.size, list(image.get_flattened_data())))

    return str(qrcode_bytes)


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
        qrcode_bytes = create_qrcode(url.format(reference_id=reference_id), file_format)
        snapshot.assert_match(_qrcode_snapshot_value(qrcode_bytes, file_format))
