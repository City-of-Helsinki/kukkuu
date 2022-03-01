from enum import Enum
from io import BytesIO

import qrcode
import qrcode.image.pil
import qrcode.image.svg


class QRCodeFileFormatEnum(Enum):
    """
    ENUM to hold the allowed values for QRCode fileformat
    """

    SVG: str = "svg"
    PNG: str = "png"


FACTORIES = {
    QRCodeFileFormatEnum.SVG.value: qrcode.image.svg.SvgImage,
    QRCodeFileFormatEnum.PNG.value: qrcode.image.pil.PilImage,
}

MIME_TYPES = {
    QRCodeFileFormatEnum.SVG.value: "image/svg+xml",
    QRCodeFileFormatEnum.PNG.value: "image/png",
}


def create_qrcode(
    input_data: str,
    file_format: QRCodeFileFormatEnum = QRCodeFileFormatEnum.SVG,
) -> bytes:
    """Create a QRCode of the given input data.

    Args:
        input_data (str): The text that will be encoded to the QRCode
        file_format (QRCodeFileFormatEnum, optional): File format of the created QRCode.
        Defaults to "svg".

    Returns:
        bytes: the QRCode image bytes
    """
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
        image_factory=FACTORIES[file_format.value],
    )
    qr.add_data(input_data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    stream = BytesIO()
    img.save(stream)
    return stream.getvalue()  # .decode()
