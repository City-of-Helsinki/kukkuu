from django.conf import settings
from hashids import Hashids

from .views import error_codes


def get_kukkuu_error_by_code(error_code):
    if not error_code:
        return None
    return next(
        (error for error, code in error_codes.items() if code == error_code), None
    )


hashids = Hashids(
    salt=settings.KUKKUU_HASHID_SALT,
    alphabet=settings.KUKKUU_HASHID_ALPHABET or "abcdefghijklmnopqrstuvwxyz",
    min_length=settings.KUKKUU_HASHID_MIN_LENGTH or 5,
)
