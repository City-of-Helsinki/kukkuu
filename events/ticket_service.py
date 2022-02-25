from typing import Tuple

from events.models import Enrolment
from kukkuu.exceptions import EnrolmentReferenceIdDoesNotExist


def check_ticket_validity(enrolment_reference_id: str) -> Tuple[Enrolment, bool]:
    """
    Returns a Tuple of enrolment and boolean of true
    if the enrolment reference id could be linked to a valid ticket
    """

    enrolment_id = Enrolment.decode_reference_id(enrolment_reference_id)
    try:
        enrolment = Enrolment.objects.get(pk=enrolment_id)
    except (Enrolment.DoesNotExist):
        raise EnrolmentReferenceIdDoesNotExist(
            "The decoded reference id does not match to any of the existing enrolments"
        )
    return (enrolment, enrolment.is_upcoming())
