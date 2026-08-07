"""
QR Code Generator.
"""

import qrcode


def generate_qr(
    data: str,
    path: str,
) -> str:
    """
    Generate QR PNG file.
    """

    image = qrcode.make(data)

    image.save(path)

    return path