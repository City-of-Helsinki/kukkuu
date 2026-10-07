import logging
from unittest.mock import MagicMock

import pytest
from graphql_relay import to_global_id

from events.factories import EventFactory, EventGroupFactory
from events.services import EventAPIService
from events.tests.mutations import COPY_EVENT_GROUP_MUTATION, COPY_EVENT_MUTATION


@pytest.mark.django_db
def test_copy_event_group_mutation(event_group_manager_api_client, project, snapshot):
    """
    Test that copying an EventGroup creates a new EventGroup with the provided
    overrides (like translations and project), while preserving the unmodified
    fields and related data (like images) from the source EventGroup.
    """
    event_group = EventGroupFactory(project=project, name="Original Name")

    variables = {
        "input": {
            "sourceEventGroupId": to_global_id("EventGroupNode", event_group.id),
            "projectId": to_global_id("ProjectNode", project.id),
            "translations": [
                {
                    "languageCode": "FI",
                    "name": "Copied Name",
                    "shortDescription": "Short desc",
                    "description": "Desc",
                }
            ],
        }
    }

    executed = event_group_manager_api_client.execute(
        COPY_EVENT_GROUP_MUTATION, variables=variables
    )

    assert "errors" not in executed

    # Verify the created object
    data = executed["data"]["copyEventGroup"]["eventGroup"]
    assert data["name"] == "Copied Name"
    assert data["project"]["id"] == to_global_id("ProjectNode", project.id)


@pytest.mark.django_db
def test_copy_event_group_requires_creation_permission(publisher_api_client, project):
    """
    Test that a user without MANAGE_EVENT_GROUPS permission cannot copy an EventGroup,
    even if they can administer the source project.
    """
    event_group = EventGroupFactory(project=project, name="Original Name")

    variables = {
        "input": {
            "sourceEventGroupId": to_global_id("EventGroupNode", event_group.id),
            "projectId": to_global_id("ProjectNode", project.id),
            "translations": [
                {
                    "languageCode": "FI",
                    "name": "Copied Name",
                    "shortDescription": "Short desc",
                    "description": "Desc",
                }
            ],
        }
    }

    executed = publisher_api_client.execute(
        COPY_EVENT_GROUP_MUTATION, variables=variables
    )

    assert "errors" in executed
    assert (
        executed["errors"][0]["message"]
        == "You do not have permission to copy event groups from this project."
    )


@pytest.mark.django_db
def test_copy_event_mutation(publisher_api_client, project, snapshot):
    """
    Test that copying an Event creates a new Event with the provided overrides
    (such as duration, capacity, participants_per_invite, translations), while
    copying over the unmodified data (like image) from the source Event, but
    stripping occurrences and other specific fields.
    """
    event_group = EventGroupFactory(project=project)
    event = EventFactory(
        project=project,
        event_group=event_group,
        name="Original Event",
        duration=60,
        participants_per_invite="FAMILY",
        capacity_per_occurrence=10,
    )

    variables = {
        "input": {
            "sourceEventId": to_global_id("EventNode", event.id),
            "projectId": to_global_id("ProjectNode", project.id),
            "eventGroupId": to_global_id("EventGroupNode", event_group.id),
            "duration": 90,
            "participantsPerInvite": "CHILD_AND_1_OR_2_GUARDIANS",
            "capacityPerOccurrence": 20,
            "translations": [
                {
                    "languageCode": "FI",
                    "name": "Copied Event",
                    "shortDescription": "Short desc",
                    "description": "Desc",
                }
            ],
        }
    }

    executed = publisher_api_client.execute(COPY_EVENT_MUTATION, variables=variables)

    assert "errors" not in executed

    data = executed["data"]["copyEvent"]["event"]
    assert data["name"] == "Copied Event"
    assert data["duration"] == 90
    assert data["participantsPerInvite"] == "CHILD_AND_1_OR_2_GUARDIANS"
    assert data["capacityPerOccurrence"] == 20
    assert data["eventGroup"]["id"] == to_global_id("EventGroupNode", event_group.id)
    assert data["project"]["id"] == to_global_id("ProjectNode", project.id)


@pytest.mark.django_db
def test_copy_image_file_logs_exception_when_image_copy_fails(caplog):
    source = EventFactory.build(pk=101)
    target = EventFactory.build(pk=202)
    source.image = MagicMock()
    source.image.name = "test.jpg"
    source.image.read.side_effect = OSError("Disk read failure")

    with caplog.at_level(logging.ERROR):
        EventAPIService._copy_image_file(source, target)

    assert "Failed to copy image from 101 to 202" in caplog.text


@pytest.mark.django_db
def test_copy_event_seeds_omitted_scalar_fields_and_translations(
    publisher_api_client, project
):
    source_event = EventFactory(
        project=project,
        name="Alkuperäinen",
        short_description="Lyhyt kuvaus FI",
        description="Pitkä kuvaus FI",
        image_alt_text="Kuva-alt FI",
        duration=45,
        participants_per_invite="FAMILY",
        capacity_per_occurrence=15,
        ready_for_event_group_publishing=True,
    )
    source_event.create_translation(
        "sv",
        name="Original SV",
        short_description="Kort SV",
        description="Lång SV",
        image_alt_text="Bild SV",
    )
    source_event.publish()
    assert source_event.published_at is not None

    variables = {
        "input": {
            "sourceEventId": to_global_id("EventNode", source_event.id),
            "projectId": to_global_id("ProjectNode", project.id),
            "participantsPerInvite": "FAMILY",
            "translations": [
                {
                    "languageCode": "FI",
                    "name": "Kopioitu FI",
                }
            ],
        }
    }

    executed = publisher_api_client.execute(COPY_EVENT_MUTATION, variables=variables)
    assert "errors" not in executed

    from events.models import Event

    copied_event = Event.objects.exclude(id=source_event.id).get()

    # Omitted scalar fields seeded from source
    assert copied_event.duration == 45
    assert copied_event.capacity_per_occurrence == 15
    assert copied_event.ready_for_event_group_publishing is True

    # Excluded fields
    assert copied_event.published_at is None
    assert copied_event.occurrences.count() == 0

    # Requested project and event group preserved
    assert copied_event.project_id == project.id
    assert copied_event.event_group_id is None

    # Translations merged and preserved
    assert (
        copied_event.safe_translation_getter("name", language_code="fi")
        == "Kopioitu FI"
    )
    assert (
        copied_event.safe_translation_getter("description", language_code="fi")
        == "Pitkä kuvaus FI"
    )
    assert (
        copied_event.safe_translation_getter("name", language_code="sv")
        == "Original SV"
    )
    assert (
        copied_event.safe_translation_getter("description", language_code="sv")
        == "Lång SV"
    )


@pytest.mark.django_db
def test_create_event_service_seeds_all_omitted_scalars(project, monkeypatch):
    from unittest.mock import MagicMock

    source_event = EventFactory(
        project=project,
        name="Lähde",
        duration=75,
        participants_per_invite="CHILD_AND_GUARDIAN",
        capacity_per_occurrence=30,
        ready_for_event_group_publishing=True,
    )

    info = MagicMock()
    info.context.user.uuid = "test-user"
    monkeypatch.setattr(
        EventAPIService, "resolve_event_target", lambda *args, **kwargs: (project, None)
    )

    kwargs = {
        "project_id": project.id,
    }
    copied_event = EventAPIService.create_event(info, kwargs, source_event=source_event)

    assert copied_event.duration == 75
    assert copied_event.participants_per_invite == "CHILD_AND_GUARDIAN"
    assert copied_event.capacity_per_occurrence == 30
    assert copied_event.ready_for_event_group_publishing is True
    assert copied_event.safe_translation_getter("name", language_code="fi") == "Lähde"


@pytest.mark.django_db
def test_copy_event_group_seeds_omitted_translations(
    event_group_manager_api_client, project
):
    source_group = EventGroupFactory(
        project=project,
        name="Ryhmä FI",
        short_description="Lyhyt FI",
        description="Kuvaus FI",
        image_alt_text="Alt FI",
    )
    source_group.create_translation(
        "sv",
        name="Grupp SV",
        short_description="Kort SV",
        description="Beskrivning SV",
        image_alt_text="Bild SV",
    )
    source_group.publish()
    assert source_group.published_at is not None

    variables = {
        "input": {
            "sourceEventGroupId": to_global_id("EventGroupNode", source_group.id),
            "projectId": to_global_id("ProjectNode", project.id),
            "translations": [
                {
                    "languageCode": "FI",
                    "name": "Uusi Ryhmä FI",
                }
            ],
        }
    }

    executed = event_group_manager_api_client.execute(
        COPY_EVENT_GROUP_MUTATION, variables=variables
    )
    assert "errors" not in executed

    from events.models import EventGroup

    copied_group = EventGroup.objects.exclude(id=source_group.id).get()

    # Excluded fields
    assert copied_group.published_at is None
    assert copied_group.events.count() == 0

    # Requested project preserved
    assert copied_group.project_id == project.id

    # Translations merged and preserved
    assert (
        copied_group.safe_translation_getter("name", language_code="fi")
        == "Uusi Ryhmä FI"
    )
    assert (
        copied_group.safe_translation_getter("description", language_code="fi")
        == "Kuvaus FI"
    )
    assert (
        copied_group.safe_translation_getter("name", language_code="sv") == "Grupp SV"
    )
    assert (
        copied_group.safe_translation_getter("description", language_code="sv")
        == "Beskrivning SV"
    )
