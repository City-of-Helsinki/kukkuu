from datetime import timedelta
from typing import Tuple

from django.conf import settings
from django.utils import timezone

from events.models import Enrolment
from kukkuu.exceptions import EnrolmentReferenceIdDoesNotExist


def check_ticket_validity(enrolment_reference_id: str) -> Tuple[Enrolment, bool]:
    """
    Returns a Tuple of enrolment and boolean of true
    if the enrolment reference id could be linked to a valid ticket
    """

    enrolment_id = Enrolment.decode_reference_id(enrolment_reference_id)
    try:
        enrolment = Enrolment.objects.with_end_time().get(pk=enrolment_id)
    except Enrolment.DoesNotExist:
        raise EnrolmentReferenceIdDoesNotExist(
            "The decoded reference id does not match to any of the existing enrolments"
        )
    start = enrolment.occurrence.time - timedelta(
        minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY
    )
    end = enrolment.end_time + timedelta(
        minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY
    )
    valid = start <= timezone.now() <= end
    return enrolment, valid
