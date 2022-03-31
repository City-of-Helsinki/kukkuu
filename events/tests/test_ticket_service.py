from datetime import datetime

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
        (datetime(2020, 11, 11, 12, tzinfo=timezone.now().tzinfo), True),  # Present
        (datetime(2020, 11, 11, 13, tzinfo=timezone.now().tzinfo), True),  # +1h
        (datetime(2020, 11, 11, 11, tzinfo=timezone.now().tzinfo), True),  # -1h
        (datetime(2020, 11, 13, 12, tzinfo=timezone.now().tzinfo), True),  # +1d
        (datetime(2020, 11, 10, 12, tzinfo=timezone.now().tzinfo), False),  # -1d
    ],
)
@pytest.mark.django_db
def test_check_ticket_validity(project, occurrence_time, expected):
    """Tickets are show valid for the whole day on the occurrence day."""
    occurrence = OccurrenceFactory(time=occurrence_time)
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
