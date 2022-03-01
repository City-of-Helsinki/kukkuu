from datetime import timedelta

import pytest
from django.utils import timezone

from events.factories import EnrolmentFactory, OccurrenceFactory
from events.ticket_service import check_ticket_validity
from kukkuu.exceptions import (
    EnrolmentReferenceIdDoesNotExist,
    IllegalEnrolmentReferenceId,
)


@pytest.mark.django_db
def test_check_ticket_validity():
    upcoming_occurrence = OccurrenceFactory(time=timezone.now() + timedelta(days=1))
    valid_enrolment = EnrolmentFactory(occurrence=upcoming_occurrence)
    enrolment, validity = check_ticket_validity(valid_enrolment.reference_id)
    assert enrolment == valid_enrolment
    assert validity is True

    past_occurrence = OccurrenceFactory(time=timezone.now() - timedelta(days=1))
    invalid_enrolment = EnrolmentFactory(occurrence=past_occurrence)
    enrolment, validity = check_ticket_validity(invalid_enrolment.reference_id)
    assert enrolment == invalid_enrolment
    assert validity is False


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
