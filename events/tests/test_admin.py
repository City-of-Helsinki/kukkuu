from datetime import timedelta
from unittest import mock

import pytest
from django.contrib.admin import helpers
from django.contrib.admin.sites import AdminSite
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from events.admin import EventGroupAdmin, EventGroupForm, OccurrenceAdmin
from events.factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    OccurrenceFactory,
)
from events.models import Event, EventGroup, Occurrence
from kukkuu.consts import DATA_VALIDATION_ERROR
from projects.factories import ProjectFactory

PUBLISH_TEMPLATE = "admin/events/publish_with_registration_opens_at.html"


class MockRequest:
    pass


@pytest.fixture
def mock_event_notifications():
    with mock.patch.object(
        Event, "_send_event_notifications_to_guardians_in_background"
    ) as mocked:
        yield mocked


@pytest.fixture
def mock_event_group_notifications():
    with mock.patch.object(
        EventGroup, "_send_event_group_notifications_to_guardians_in_background"
    ) as mocked:
        yield mocked


@pytest.mark.django_db
def test_event_group_form_valid_when_events_in_same_project():
    project = ProjectFactory(year=3000)
    event1 = EventFactory(project=project)
    event2 = EventFactory(project=project)

    form_data = {
        "project": project.id,
        "name_fi": "Testiryhmä",
        "events": [event1.id, event2.id],
    }
    form = EventGroupForm(data=form_data)
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_event_group_form_invalid_when_events_in_different_project():
    project1 = ProjectFactory(year=3001)
    project2 = ProjectFactory(year=3002)
    event1 = EventFactory(project=project1)
    event2 = EventFactory(project=project2)

    form_data = {
        "project": project1.id,
        "name_fi": "Testiryhmä",
        "events": [event1.id, event2.id],
    }
    form = EventGroupForm(data=form_data)
    assert not form.is_valid()
    assert "events" in form.errors
    expected_error = _(
        "The event group and its events must belong to the same project."
    )
    assert expected_error in form.errors["events"]
    assert any(
        error.code == DATA_VALIDATION_ERROR for error in form.errors.as_data()["events"]
    )


@pytest.mark.django_db
def test_event_group_form_valid_without_events():
    project = ProjectFactory(year=3003)
    form_data = {
        "project": project.id,
        "name_fi": "Testiryhmä",
        "events": [],
    }
    form = EventGroupForm(data=form_data)
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_event_group_form_update_mismatched_project():
    project1 = ProjectFactory(year=3004)
    project2 = ProjectFactory(year=3005)
    event_group = EventGroupFactory(project=project1)
    event = EventFactory(project=project1, event_group=event_group)

    # Change the project to project2 while keeping event from project1
    form_data = {
        "project": project2.id,
        "name_fi": "Päivitetty ryhmä",
        "events": [event.id],
    }
    form = EventGroupForm(data=form_data, instance=event_group)
    assert not form.is_valid()
    assert "events" in form.errors
    expected_error = _(
        "The event group and its events must belong to the same project."
    )
    assert expected_error in form.errors["events"]


@pytest.mark.django_db
def test_event_group_admin_save_model_flow():
    project = ProjectFactory(year=3006)
    event1 = EventFactory(project=project)
    event2 = EventFactory(project=project)

    form_data = {
        "project": project.id,
        "name_fi": "Admin ryhmä",
        "events": [event1.id, event2.id],
    }
    form = EventGroupForm(data=form_data)
    assert form.is_valid()

    admin = EventGroupAdmin(model=form.Meta.model, admin_site=AdminSite())
    obj = form.save(commit=False)
    admin.save_model(request=MockRequest(), obj=obj, form=form, change=False)

    assert obj.pk is not None
    assert set(obj.events.all()) == {event1, event2}


def _registration_opens_at_form_fields(registration_opens_at) -> dict:
    """
    Build the admin form POST fields for a `registration_opens_at` datetime.

    The admin renders a DateTimeField as a split date/time widget, so the
    value cannot be posted as a single field: it has to be sent as the
    `_0` (date) and `_1` (time) sub-fields, in the current time zone, which
    is what the admin form interprets them in.
    """
    local_registration_opens_at = timezone.localtime(registration_opens_at)
    return {
        "registration_opens_at_0": local_registration_opens_at.strftime("%Y-%m-%d"),
        "registration_opens_at_1": local_registration_opens_at.strftime("%H:%M:%S"),
    }


def _post_admin_publish_action(
    client, objs: list[Event] | list[EventGroup], registration_opens_at=None
):
    """
    Post the "publish" admin action for the given same type objects to their changelist

    Without `registration_opens_at` admin responds with the intermediate page
    asking for it. With it, the data is submitted (`apply`).
    """
    model = type(objs[0])
    assert all(isinstance(obj, model) for obj in objs)
    data = {
        "action": "publish",
        helpers.ACTION_CHECKBOX_NAME: [obj.pk for obj in objs],
    }
    if registration_opens_at:
        data["apply"] = "1"
        data.update(_registration_opens_at_form_fields(registration_opens_at))
    return client.post(
        reverse(f"admin:events_{model._meta.model_name}_changelist"), data
    )


def _assert_publish_intermediate_page(response, objs):
    """
    Assert that the response is the intermediate page of the "publish" action
    (i.e. nothing was published yet) listing exactly the given objects.
    """
    assert response.status_code == 200
    assert PUBLISH_TEMPLATE in (t.name for t in response.templates)
    assert list(response.context["queryset"]) == list(objs)


@pytest.mark.django_db
def test_event_admin_change_form_can_edit_registration_opens_at(admin_client, past):
    """Django admin can correct the registration opening time of a published
    event, even into the past.
    """
    event = EventFactory(published_at=past, registration_opens_at=now())

    response = admin_client.post(
        reverse("admin:events_event_change", args=[event.pk]),
        {
            "project": event.project.pk,
            "organisation": event.organisation.pk,
            "name": event.name,
            "short_description": event.short_description,
            "description": event.description,
            "capacity_per_occurrence": 10,
            "participants_per_invite": event.participants_per_invite,
            "ready_for_event_group_publishing": "on",  # browser's post for check box
            "ticket_system": Event.INTERNAL,
            **_registration_opens_at_form_fields(past),
            "occurrences-TOTAL_FORMS": "0",
            "occurrences-INITIAL_FORMS": "0",
        },
    )

    assert response.status_code == 302  # 302 = saved, 200 = form errors
    event.refresh_from_db()
    assert event.registration_opens_at == past
    assert event.published_at == past


@pytest.mark.django_db
@pytest.mark.parametrize(
    "obj_factory",
    [EventFactory, EventGroupFactory],
    ids=["event", "event_group"],
)
def test_admin_publish_action_asks_registration_opens_at(admin_client, obj_factory):
    """
    Test that Django admin "publish" action goes to an intermediate page
    asking for the registration opening time first instead of publishing
    the events or event groups.
    """
    objs = obj_factory.create_batch(2)

    response = _post_admin_publish_action(admin_client, objs)

    _assert_publish_intermediate_page(response, objs)
    for obj in objs:
        obj.refresh_from_db()
        assert not obj.is_published()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "obj_factory", [EventFactory, EventGroupFactory], ids=["event", "event_group"]
)
def test_admin_publish_action_rejects_past_registration_opens_at(
    admin_client, obj_factory
):
    obj = obj_factory()

    response = _post_admin_publish_action(
        admin_client, [obj], registration_opens_at=now() - timedelta(seconds=1)
    )

    _assert_publish_intermediate_page(response, [obj])
    assert response.context["form"].errors["registration_opens_at"]
    obj.refresh_from_db()
    assert not obj.is_published()


@pytest.mark.django_db
def test_event_admin_publish_action(
    admin_client, past, future, mock_event_notifications
):
    """The event action publishes the selected events, also already published ones
    and group members, and leaves the other events unchanged.
    """
    unpublished_event = EventFactory()
    published_group_event = EventFactory(
        event_group=EventGroupFactory(published_at=past),
        published_at=past,
        registration_opens_at=past,
    )
    not_selected_group_event = EventFactory(
        event_group=published_group_event.event_group,
        published_at=past,
        registration_opens_at=past,
    )

    events_to_publish = [unpublished_event, published_group_event]
    response = _post_admin_publish_action(
        admin_client, events_to_publish, registration_opens_at=future
    )

    assert response.status_code == 302
    for event in events_to_publish:
        event.refresh_from_db()
        assert event.published_at == now()
        assert event.registration_opens_at == future
    not_selected_group_event.refresh_from_db()
    assert not_selected_group_event.published_at == past
    assert not_selected_group_event.registration_opens_at == past
    assert mock_event_notifications.call_count == len(events_to_publish)


@pytest.mark.django_db
def test_event_group_admin_publish_action(
    admin_client, past, future, mock_event_group_notifications
):
    """The event group action sets the registration opening time only to the
    unpublished events of the event groups.
    """
    new_event_group = EventGroupFactory()
    new_group_event = EventFactory(event_group=new_event_group)
    published_event_group = EventGroupFactory(published_at=past)
    published_event = EventFactory(
        event_group=published_event_group,
        published_at=past,
        registration_opens_at=past,
    )
    unpublished_event = EventFactory(event_group=published_event_group)

    event_groups_to_publish = [new_event_group, published_event_group]
    response = _post_admin_publish_action(
        admin_client, event_groups_to_publish, registration_opens_at=future
    )

    assert response.status_code == 302
    for event in new_group_event, unpublished_event:
        event.refresh_from_db()
        assert event.published_at == now()
        assert event.registration_opens_at == future
    published_event.refresh_from_db()
    assert published_event.published_at == past
    assert published_event.registration_opens_at == past
    assert mock_event_group_notifications.call_count == len(event_groups_to_publish)


@pytest.mark.django_db
def test_event_group_admin_publish_action_rejects_republish_without_unpublished_events(
    admin_client, past, future, mock_event_group_notifications
):
    event_group = EventGroupFactory(published_at=past)
    event = EventFactory(
        event_group=event_group, published_at=past, registration_opens_at=past
    )

    response = _post_admin_publish_action(
        admin_client, [event_group], registration_opens_at=future
    )

    assert response.status_code == 302
    event_group.refresh_from_db()
    event.refresh_from_db()
    assert event_group.published_at == past
    assert event.registration_opens_at == past
    mock_event_group_notifications.assert_not_called()
    response = admin_client.get(response.url)
    assert "Event group is already published." in response.content.decode()


@pytest.mark.django_db
def test_occurrence_admin_get_queryset_annotates_reserved_seats(rf):
    occurrence = OccurrenceFactory(capacity_override=10)
    EnrolmentFactory(
        occurrence=occurrence,
        extra_children_count=1,
        extra_guardians_count=0,
    )

    site = AdminSite()
    admin_instance = OccurrenceAdmin(Occurrence, site)
    request = rf.get("/admin/events/occurrence/")
    qs = admin_instance.get_queryset(request)
    obj = qs.get(pk=occurrence.pk)

    assert hasattr(obj, "reserved_seats")
    assert obj.reserved_seats == 3
    assert admin_instance.get_enrolments(obj) == "3 / 10"
