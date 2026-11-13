from django.conf import settings

from venues.models import Venue


def get_system_venue() -> Venue:
    venue = Venue.objects.filter(is_system=True).first()
    if not venue:
        venue = Venue.objects.create_translatable_object(
            is_system=True,
            project=None,
            translations=[
                {
                    "language_code": lang_code,
                    "name": settings.KUKKUU_DEFAULT_VENUE_NAME,
                }
                for lang_code in settings.PARLER_SUPPORTED_LANGUAGE_CODES
            ],
        )
    return venue
