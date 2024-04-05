from datetime import date
from typing import Union

import pytest
from click import UUID
from django.contrib.auth import get_user_model
from django.core import mail
from freezegun import freeze_time

from events.factories import (
    EnrolmentFactory,
    OccurrenceFactory,
    TicketSystemPasswordFactory,
)
from events.models import Enrolment
from users.factories import GuardianFactory

from ..factories import (
    ChildFactory,
    ChildWithGuardianFactory,
    ChildWithTwoGuardiansFactory,
    RelationshipFactory,
)
from ..models import Child, Guardian

User = get_user_model()


def _set_guardian_email(guardian: Guardian, email: str) -> Guardian:
    guardian.email = email
    guardian.save()
    return guardian


@pytest.mark.django_db
def test_child_creation(project):
    ChildFactory(project=project)

    assert Child.objects.count() == 1


@pytest.mark.django_db
def test_relationship_creation(project):
    RelationshipFactory(child__project=project)

    assert Child.objects.count() == 1
    assert User.objects.count() == 1


@pytest.mark.parametrize("test_queryset", (False, True))
@pytest.mark.django_db
def test_enrolment_handling_when_child_deleted(
    past, future, event, test_queryset, notification_template_occurrence_unenrolment_fi
):
    past_occurrence = OccurrenceFactory(event=event, time=past)
    future_occurrence = OccurrenceFactory(event=event, time=future)

    child, another_child = ChildWithGuardianFactory.create_batch(2)
    past_enrolment = EnrolmentFactory(child=child, occurrence=past_occurrence)
    future_enrolment = EnrolmentFactory(child=child, occurrence=future_occurrence)
    another_child_past_enrolment = EnrolmentFactory(
        child=another_child, occurrence=past_occurrence
    )
    another_child_future_enrolment = EnrolmentFactory(
        child=another_child, occurrence=future_occurrence
    )

    if test_queryset:
        Child.objects.filter(id=child.id).delete()
    else:
        child.delete()

    past_enrolment.refresh_from_db()
    assert past_enrolment.child is None
    with pytest.raises(Enrolment.DoesNotExist):
        future_enrolment.refresh_from_db()

    # another child's enrolments should be unaffected
    another_child_past_enrolment.refresh_from_db()
    assert another_child_past_enrolment.child == another_child
    another_child_future_enrolment.refresh_from_db()
    assert another_child_future_enrolment.child == another_child

    assert len(mail.outbox) == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field_name,orig_field_value,later_field_value,should_change_hash",
    [
        ("name", "Peter", "Mary", False),
        ("birthyear", 2021, 2022, True),
        ("postal_code", "12345", "10100", True),
    ],
)
def test_child_birthyear_postal_code_guardian_emails_hash(
    field_name: str,
    orig_field_value: Union[str, date],
    later_field_value: Union[str, date],
    should_change_hash: bool,
):
    child: Child = ChildWithGuardianFactory()
    setattr(child, field_name, orig_field_value)
    orig_hash = child.birthyear_postal_code_guardian_emails_hash
    setattr(child, field_name, later_field_value)
    later_hash = child.birthyear_postal_code_guardian_emails_hash
    assert should_change_hash == (orig_hash != later_hash)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field_name,orig_field_value,later_field_value,should_change_hash",
    [
        ("name", "Peter", "Mary", True),
        ("birthyear", 2021, 2022, True),
        ("postal_code", "12345", "10100", True),
    ],
)
def test_child_name_birthyear_postal_code_guardian_emails_hash(
    field_name: str,
    orig_field_value: Union[str, date],
    later_field_value: Union[str, date],
    should_change_hash: bool,
):
    child = ChildWithGuardianFactory()
    setattr(child, field_name, orig_field_value)
    orig_hash = child.name_birthyear_postal_code_guardian_emails_hash
    setattr(child, field_name, later_field_value)
    later_hash = child.name_birthyear_postal_code_guardian_emails_hash
    assert should_change_hash == (orig_hash != later_hash)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "hash_property_name",
    [
        "birthyear_postal_code_guardian_emails_hash",
        "name_birthyear_postal_code_guardian_emails_hash",
    ],
)
def test_child_hashes_email_change(hash_property_name: str):
    child: Child = ChildWithTwoGuardiansFactory()
    _set_guardian_email(child.guardians.first(), "a@example.org")
    _set_guardian_email(child.guardians.last(), "b@example.org")
    assert sorted(guardian.email for guardian in child.guardians.all()) == [
        "a@example.org",
        "b@example.org",
    ]
    assert child.guardians.first().email != child.guardians.last().email
    hash1 = getattr(child, hash_property_name)
    _set_guardian_email(child.guardians.first(), "c@example.org")
    assert child.guardians.first().email == "c@example.org"
    hash2 = getattr(child, hash_property_name)
    assert hash1 != hash2
    _set_guardian_email(child.guardians.last(), "d@example.org")
    assert child.guardians.last().email == "d@example.org"
    hash3 = getattr(child, hash_property_name)
    assert hash2 != hash3
    child.guardians.first().delete()
    assert len(child.guardians.all()) == 1
    hash4 = getattr(child, hash_property_name)
    assert hash3 != hash4
    child.guardians.last().delete()
    assert len(child.guardians.all()) == 0
    hash5 = getattr(child, hash_property_name)
    assert hash4 != hash5
    assert len({hash1, hash2, hash3, hash4, hash5}) == 5


@pytest.mark.django_db
def test_child_clear_gdpr_sensitive_data_fields():
    child: Child = ChildFactory(name="Initial Name")
    child.clear_gdpr_sensitive_data_fields()
    child.refresh_from_db()
    assert child.name == ""


@pytest.mark.django_db
@freeze_time("2020-11-11 12:00:00")
def test_child_serialize(snapshot, project):
    guardian = GuardianFactory(
        id=UUID("8dff3da4-a329-4b81-971a-bc509df679b1"),
        user__uuid=UUID("fa354000-3c0c-11eb-86c5-acde48001122"),
    )
    user = guardian.user
    user.administered_projects = [project]
    user.save()
    child = ChildWithGuardianFactory(relationship__guardian=guardian)
    EnrolmentFactory.create_batch(5, child=child)
    TicketSystemPasswordFactory.create_batch(5, child=child)
    user.refresh_from_db()
    snapshot.assert_match(user.serialize())
