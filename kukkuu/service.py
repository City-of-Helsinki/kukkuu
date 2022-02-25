from django.conf import settings
from hashids import Hashids


def get_hashid_service():
    return Hashids(
        salt=settings.KUKKUU_HASHID_SALT,
        alphabet=settings.KUKKUU_HASHID_ALPHABET or "abcdefghijklmnopqrstuvwxyz",
        min_length=settings.KUKKUU_HASHID_MIN_LENGTH or 5,
    )
