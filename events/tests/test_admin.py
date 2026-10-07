from datetime import timedelta
from unittest import mock

import pytest
from django.contrib.admin import helpers
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now

from events.factories import EventFactory, EventGroupFactory
from events.models import Event, EventGroup

PUBLISH_TEMPLATE = "admin/events/publish_with_registration_opens_at.html"


@pytest.fixture(autouse=True)
def autouse_db(db):
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


def _registration_opens_at_post_data(registration_opens_at) -> dict:
    local_registration_opens_at = timezone.localtime(registration_opens_at)
    return {
        "registration_opens_at_0": local_registration_opens_at.strftime("%Y-%m-%d"),
        "registration_opens_at_1": local_registration_opens_at.strftime("%H:%M:%S"),
    }


def _post_publish_action(client, objs, registration_opens_at=None):
    """
    Post the publish admin action of the objects' changelist. Without the
    registration opening time, the intermediate page is requested.
    """
    model = type(objs[0])
    data = {
        "action": "publish",
        helpers.ACTION_CHECKBOX_NAME: [obj.pk for obj in objs],
    }
    if registration_opens_at:
        data["apply"] = "1"
        data.update(_registration_opens_at_post_data(registration_opens_at))
    return client.post(
        reverse(f"admin:events_{model._meta.model_name}_changelist"), data
    )


def _assert_publish_page(response, objs):
    assert response.status_code == 200
    assert PUBLISH_TEMPLATE in (t.name for t in response.templates)
    assert list(response.context["queryset"]) == list(objs)


def test_event_admin_change_form_can_edit_registration_opens_at(admin_client, past):
    """Django admin can correct the registration opening time of a published
    event, also into the past.
    """
    event = EventFactory(published_at=past, registration_opens_at=now())

    response = admin_client.post(
        reverse("admin:events_event_change", args=[event.pk]),
        {
            "project": event.project.pk,
            "name": event.name,
            "short_description": event.short_description,
            "description": event.description,
            "capacity_per_occurrence": 10,
            "participants_per_invite": event.participants_per_invite,
            "ready_for_event_group_publishing": "on",
            "ticket_system": Event.INTERNAL,
            **_registration_opens_at_post_data(past),
            "occurrences-TOTAL_FORMS": "0",
            "occurrences-INITIAL_FORMS": "0",
        },
    )

    assert response.status_code == 302
    event.refresh_from_db()
    assert event.registration_opens_at == past
    assert event.published_at == past


@pytest.mark.parametrize(
    "objs_factory",
    [
        lambda: EventFactory.create_batch(2),
        lambda: EventGroupFactory.create_batch(2),
    ],
    ids=["event", "event_group"],
)
def test_admin_publish_action_asks_registration_opens_at(admin_client, objs_factory):
    objs = objs_factory()

    response = _post_publish_action(admin_client, objs)

    _assert_publish_page(response, objs)
    for obj in objs:
        obj.refresh_from_db()
        assert not obj.is_published()


@pytest.mark.parametrize(
    "obj_factory", [EventFactory, EventGroupFactory], ids=["event", "event_group"]
)
def test_admin_publish_action_rejects_past_registration_opens_at(
    admin_client, obj_factory
):
    obj = obj_factory()

    response = _post_publish_action(
        admin_client, [obj], registration_opens_at=now() - timedelta(seconds=1)
    )

    _assert_publish_page(response, [obj])
    assert response.context["form"].errors["registration_opens_at"]
    obj.refresh_from_db()
    assert not obj.is_published()
    assert not Event.objects.filter(registration_opens_at__isnull=False).exists()


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

    response = _post_publish_action(
        admin_client,
        [unpublished_event, published_group_event],
        registration_opens_at=future,
    )

    assert response.status_code == 302
    for event in (unpublished_event, published_group_event):
        event.refresh_from_db()
        assert event.published_at == now()
        assert event.registration_opens_at == future
    not_selected_group_event.refresh_from_db()
    assert not_selected_group_event.published_at == past
    assert not_selected_group_event.registration_opens_at == past
    assert mock_event_notifications.call_count == 2


def test_event_group_admin_publish_action(
    admin_client, past, future, mock_event_group_notifications
):
    """The event group action sets the registration opening time to all the events
    on the initial publication and only to the unpublished events on republication.
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

    response = _post_publish_action(
        admin_client,
        [new_event_group, published_event_group],
        registration_opens_at=future,
    )

    assert response.status_code == 302
    for event in (new_group_event, unpublished_event):
        event.refresh_from_db()
        assert event.published_at == now()
        assert event.registration_opens_at == future
    published_event.refresh_from_db()
    assert published_event.published_at == past
    assert published_event.registration_opens_at == past
    assert mock_event_group_notifications.call_count == 2


def test_event_group_admin_publish_action_rejects_republish_without_unpublished_events(
    admin_client, past, future, mock_event_group_notifications
):
    event_group = EventGroupFactory(published_at=past)
    event = EventFactory(
        event_group=event_group, published_at=past, registration_opens_at=past
    )

    response = _post_publish_action(
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
