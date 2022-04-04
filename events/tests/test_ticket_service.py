from datetime import timedelta

import pytest
from django.utils import timezone
from freezegun import freeze_time

from events.factories import EnrolmentFactory, OccurrenceFactory
from events.ticket_service import check_ticket_validity
from kukkuu.exceptions import (
    EnrolmentReferenceIdDoesNotExist,
    IllegalEnrolmentReferenceId,
)


@freeze_time("2020-11-11 12:00:00")
@pytest.mark.parametrize(
    "occurrence_time, expected",
    [
        (timedelta(minutes=16), False),  # Starts in 16 minutes
        (timedelta(minutes=15), True),  # Starts in 15 minutes
        (timedelta(minutes=0), True),  # Starts now
        (timedelta(minutes=-30), True),  # Ended 15 minutes ago
        (timedelta(minutes=-31), False),  # Ended 16 minutes ago
    ],
)
@pytest.mark.django_db
def test_check_ticket_validity(project, occurrence_time, expected, settings):
    """Tickets are show valid for the whole day on the occurrence day."""
    settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY = 15
    occurrence = OccurrenceFactory(
        time=timezone.now() + occurrence_time, event__duration=15
    )
    expected_enrolment = EnrolmentFactory(occurrence=occurrence)
    enrolment, validity = check_ticket_validity(expected_enrolment.reference_id)
    assert enrolment == expected_enrolment
    assert validity is expected


@pytest.mark.django_db
def test_illegal_enrolment_reference_id():
    with pytest.raises(IllegalEnrolmentReferenceId):
        check_ticket_validity("illegal code")


@pytest.mark.django_db
def test_enrolment_reference_does_not_exist():
    enrolment = EnrolmentFactory()
    reference_id = enrolment.reference_id
    enrolment.delete()
    with pytest.raises(EnrolmentReferenceIdDoesNotExist):
        check_ticket_validity(reference_id)
