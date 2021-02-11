import pytest
from django.contrib.auth import get_user_model
from django.core import mail

from events.factories import EnrolmentFactory, OccurrenceFactory
from events.models import Enrolment

from ..factories import ChildFactory, ChildWithGuardianFactory, RelationshipFactory
from ..models import Child

User = get_user_model()


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
