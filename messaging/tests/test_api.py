from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.core import mail
from django.utils.timezone import now
from guardian.shortcuts import assign_perm

from children.factories import ChildWithGuardianFactory
from common.notification_service import SMSNotificationService
from common.tests.utils import assert_match_error_code, assert_permission_denied
from common.utils import get_global_id
from events.factories import EventFactory, OccurrenceFactory
from kukkuu.consts import (
    DATA_VALIDATION_ERROR,
    MESSAGE_ALREADY_SENT_ERROR,
    OBJECT_DOES_NOT_EXIST_ERROR,
)
from messaging.factories import MessageFactory
from messaging.models import Message

MESSAGES_QUERY = """
query Messages(
    $projectId: ID, 
    $protocol: MessagingMessageProtocolChoices, 
    $occurrences: [ID],
    $limit: Int, 
    $offset: Int, 
    $after: String, 
    $first: Int,
    $orderBy: String
) {
    messages(
        projectId: $projectId, 
        protocol: $protocol, 
        occurrences: $occurrences,
        limit: $limit, 
        offset: $offset, 
        after: $after, 
        first: $first,
        orderBy: $orderBy
    ) {
    pageInfo {
      startCursor
      endCursor
      hasPreviousPage
      hasNextPage
    }
    count
    edges {
      node {
        project {
          year
        }
        protocol
        subject
        bodyText
        recipientSelection
        sentAt
        recipientCount
        event {
          name
        }
        occurrences {
          edges {
            node {
              time
            }
          }
        }
      }
    }
  }
}
"""  # noqa W291


def test_messages_query(snapshot, project_user_api_client, message, another_project):
    MessageFactory(project=another_project)

    executed = project_user_api_client.execute(MESSAGES_QUERY)

    snapshot.assert_match(executed)


def test_cannot_do_messages_query_unauthorized(user_api_client, message):
    executed = user_api_client.execute(MESSAGES_QUERY)

    assert_permission_denied(executed)


def test_messages_query_project_filter(
    snapshot, project_user_api_client, message, project, another_project
):
    assign_perm("admin", project_user_api_client.user, another_project)

    executed = project_user_api_client.execute(
        MESSAGES_QUERY, variables={"project_id": get_global_id(project)}
    )

    snapshot.assert_match(executed)


@pytest.mark.parametrize("protocol", [Message.SMS, Message.EMAIL])
def test_messages_query_protocol_filter(
    protocol, snapshot, project_user_api_client, project
):
    MessageFactory.create_batch(5, protocol=Message.SMS, project=project)
    MessageFactory.create_batch(5, protocol=Message.EMAIL, project=project)

    executed = project_user_api_client.execute(
        MESSAGES_QUERY, variables={"protocol": protocol.upper()}
    )
    assert all(
        edge["node"]["protocol"] == protocol.upper()
        for edge in executed["data"]["messages"]["edges"]
    )
    assert len(executed["data"]["messages"]["edges"]) == 5
    snapshot.assert_match(executed)


def test_messages_query_occurrences_filter(snapshot, project_user_api_client, project):
    occurrence1 = OccurrenceFactory(
        messages=MessageFactory.create_batch(2, project=project)
    )
    occurrence2 = OccurrenceFactory(
        messages=MessageFactory.create_batch(2, project=project)
    )
    OccurrenceFactory(messages=MessageFactory.create_batch(2, project=project))

    assert Message.objects.count() == 6

    executed = project_user_api_client.execute(
        MESSAGES_QUERY,
        variables={
            "occurrences": [
                get_global_id(occurrence) for occurrence in [occurrence1, occurrence2]
            ]
        },
    )
    assert len(executed["data"]["messages"]["edges"]) == 4
    snapshot.assert_match(executed)


@pytest.mark.parametrize("protocol", [Message.SMS, Message.EMAIL])
def test_messages_query_occurrences_and_protol_filter_together(
    protocol, project_user_api_client, project
):
    occurrence1 = OccurrenceFactory(
        messages=MessageFactory.create_batch(2, project=project, protocol=Message.SMS)
    )
    occurrence2 = OccurrenceFactory(
        messages=MessageFactory.create_batch(2, project=project, protocol=Message.EMAIL)
    )

    assert Message.objects.count() == 4

    executed = project_user_api_client.execute(
        MESSAGES_QUERY,
        variables={
            "protocol": protocol.upper(),
            "occurrences": [
                get_global_id(occurrence) for occurrence in [occurrence1, occurrence2]
            ],
        },
    )
    assert len(executed["data"]["messages"]["edges"]) == 2


def test_messages_query_pagination_with_first_and_after(
    project_user_api_client, project
):
    MessageFactory.create_batch(10, project=project)
    assert Message.objects.count() == 10
    # First 2 of 10 objects
    executed = project_user_api_client.execute(
        MESSAGES_QUERY,
        variables={"first": 2},
    )
    assert len(executed["data"]["messages"]["edges"]) == 2
    # FIXME: hasPreviousPage is not working https://github.com/graphql-python/graphene/issues/395
    # assert executed["data"]["messages"]["pageInfo"]["hasPreviousPage"] is False
    assert executed["data"]["messages"]["pageInfo"]["hasNextPage"] is True

    # Second page for next 4 objects, so 6 of 10 objects shown
    end_cursor = executed["data"]["messages"]["pageInfo"]["endCursor"]
    executed = project_user_api_client.execute(
        MESSAGES_QUERY,
        variables={
            "first": 4,
            "after": end_cursor,
        },
    )
    assert len(executed["data"]["messages"]["edges"]) == 4
    # assert executed["data"]["messages"]["pageInfo"]["hasPreviousPage"] is True
    assert executed["data"]["messages"]["pageInfo"]["hasNextPage"] is True

    # Third and the last page for next 4 objects, so 10 of 10 objects shown
    end_cursor = executed["data"]["messages"]["pageInfo"]["endCursor"]
    executed = project_user_api_client.execute(
        MESSAGES_QUERY,
        variables={
            "first": 4,
            "after": end_cursor,
        },
    )
    assert len(executed["data"]["messages"]["edges"]) == 4
    # assert executed["data"]["messages"]["pageInfo"]["hasPreviousPage"] is True
    assert executed["data"]["messages"]["pageInfo"]["hasNextPage"] is False

    # 4th page has no objects
    end_cursor = executed["data"]["messages"]["pageInfo"]["endCursor"]
    executed = project_user_api_client.execute(
        MESSAGES_QUERY,
        variables={
            "first": 4,
            "after": end_cursor,
        },
    )
    assert len(executed["data"]["messages"]["edges"]) == 0
    # assert executed["data"]["messages"]["pageInfo"]["hasPreviousPage"] is True
    assert executed["data"]["messages"]["pageInfo"]["hasNextPage"] is False


def test_messages_query_pagination_with_limit_and_offset(
    project_user_api_client, project
):
    """
    The Kukkuu Admin UI's React-Admin framework supports only
    the limit-offset pagination type. This is implemented in Kukkuu with
    `common.schema.DjangoFilterAndOffsetConnectionField`.
    """
    MessageFactory.create_batch(10, project=project)
    assert Message.objects.count() == 10
    # First 2 of 10 objects
    executed = project_user_api_client.execute(
        MESSAGES_QUERY,
        variables={"limit": 2},
    )
    assert len(executed["data"]["messages"]["edges"]) == 2
    # FIXME: hasPreviousPage is not working https://github.com/graphql-python/graphene/issues/395
    # assert executed["data"]["messages"]["pageInfo"]["hasPreviousPage"] is False
    assert executed["data"]["messages"]["pageInfo"]["hasNextPage"] is True

    # Second page for next 4 objects, so 6 of 10 objects shown
    end_cursor = 2
    executed = project_user_api_client.execute(
        MESSAGES_QUERY,
        variables={
            "limit": 4,
            "offset": end_cursor,
        },
    )
    assert len(executed["data"]["messages"]["edges"]) == 4
    # assert executed["data"]["messages"]["pageInfo"]["hasPreviousPage"] is True
    assert executed["data"]["messages"]["pageInfo"]["hasNextPage"] is True

    # Third and the last page for next 4 objects, so 10 of 10 objects shown
    end_cursor = 2 + 4
    executed = project_user_api_client.execute(
        MESSAGES_QUERY,
        variables={
            "limit": 4,
            "offset": end_cursor,
        },
    )
    assert len(executed["data"]["messages"]["edges"]) == 4
    # assert executed["data"]["messages"]["pageInfo"]["hasPreviousPage"] is True
    assert executed["data"]["messages"]["pageInfo"]["hasNextPage"] is False

    # 4th page has no objects
    end_cursor = 2 + 4 + 4
    executed = project_user_api_client.execute(
        MESSAGES_QUERY,
        variables={
            "limit": 4,
            "offset": end_cursor,
        },
    )
    assert len(executed["data"]["messages"]["edges"]) == 0
    # assert executed["data"]["messages"]["pageInfo"]["hasPreviousPage"] is True
    assert executed["data"]["messages"]["pageInfo"]["hasNextPage"] is False


@pytest.mark.parametrize(
    "order_by_criteria", ["created_at", "-created_at", "sent_at", "-sent_at"]
)
def test_messages_query_order_by(order_by_criteria, project_user_api_client, project):
    for days in range(0, 5, 1):
        t = now() - timedelta(days=days)
        MessageFactory(project=project, sent_at=t, created_at=t)
    executed = project_user_api_client.execute(
        MESSAGES_QUERY,
        variables={"orderBy": order_by_criteria},
    )
    messages = [edge["node"] for edge in executed["data"]["messages"]["edges"]]
    assert len(messages) == 5
    assert [
        message.subject for message in Message.objects.all().order_by(order_by_criteria)
    ] == [message["subject"] for message in messages]


MESSAGE_QUERY = """
query Message($id: ID!) {
  message(id: $id){
    project {
      year
    }
    subject
    bodyText
    recipientSelection
    sentAt
    recipientCount
    event {
      name
    }
    occurrences {
      edges {
        node {
          time
        }
      }
    }
  }
}
"""


def test_message_query(snapshot, project_user_api_client, message):
    executed = project_user_api_client.execute(
        MESSAGE_QUERY, variables={"id": get_global_id(message)}
    )

    snapshot.assert_match(executed)


def test_cannot_do_message_query_unauthorized(user_api_client, message):
    executed = user_api_client.execute(
        MESSAGE_QUERY, variables={"id": get_global_id(message)}
    )

    assert_permission_denied(executed)


def test_cannot_do_message_query_unauthorized_wrong_project(
    snapshot, wrong_project_api_client, message
):
    executed = wrong_project_api_client.execute(
        MESSAGE_QUERY, variables={"id": get_global_id(message)}
    )

    snapshot.assert_match(executed)


ADD_MESSAGE_MUTATION = """
mutation AddMessage($input: AddMessageMutationInput!) {
  addMessage(input: $input) {
    message {
      protocol
      translations {
        languageCode
        subject
        bodyText
      }
      sentAt
      recipientSelection
      recipientCount
      project {
        year
      }
      event {
        name
      }
      occurrences {
        edges {
          node {
            time
          }
        }
      }
    }
  }
}
"""


def get_add_message_variables(
    project,
    event=None,
    occurrences=None,
    recipient="ALL",
    protocol="EMAIL",
    send_directly=False,
):
    variables = {
        "input": {
            "translations": [
                {
                    "subject": "Testiotsikko",
                    "bodyText": "Testiteksti",
                    "languageCode": "FI",
                }
            ],
            "recipientSelection": recipient,
            "projectId": get_global_id(project),
            "protocol": protocol,
            "sendDirectly": send_directly,
        }
    }
    if event:
        variables["input"]["eventId"] = get_global_id(event)
    if occurrences is not None:
        variables["input"]["occurrenceIds"] = [get_global_id(o) for o in occurrences]
    if send_directly:
        variables["input"]["sendDirectly"] = send_directly
    return variables


@pytest.mark.parametrize("event_selection", (None, "event", "occurrences"))
@pytest.mark.django_db
def test_add_message(snapshot, project_user_api_client, project, event_selection):
    if event_selection == "event":
        variables = get_add_message_variables(
            project, event=EventFactory(published_at=now())
        )
    elif event_selection == "occurrences":
        event = EventFactory(published_at=now())
        occurrences = OccurrenceFactory.create_batch(3, event=event)
        variables = get_add_message_variables(
            project, event=event, occurrences=occurrences
        )
    else:
        variables = get_add_message_variables(project)

    executed = project_user_api_client.execute(
        ADD_MESSAGE_MUTATION, variables=variables
    )

    snapshot.assert_match(executed)


@pytest.mark.parametrize("protocol", [Message.EMAIL, Message.SMS])
@patch.object(SMSNotificationService, "send_sms")
def test_send_email_directly_with_add_message(
    mock_send_sms, protocol, project, project_user_api_client
):
    ChildWithGuardianFactory()

    variables = get_add_message_variables(
        project, protocol=protocol.upper(), send_directly=True
    )
    project_user_api_client.execute(ADD_MESSAGE_MUTATION, variables=variables)
    if protocol == Message.SMS.upper():
        mock_send_sms.assert_called_once()
    elif protocol == Message.EMAIL.upper():
        assert len(mail.outbox) == 1


@pytest.mark.parametrize("event_selection", ("event", "event_and_occurrences"))
@pytest.mark.django_db
def test_cannot_add_message_with_event_for_invited_group_message(
    project_user_api_client, event_selection, project
):
    event = EventFactory(published_at=now())
    occurrences = []

    if event_selection == "event_and_occurrences":
        occurrences = [OccurrenceFactory(event=event)]

    variables = get_add_message_variables(
        project,
        event=event,
        occurrences=occurrences,
        recipient="INVITED",
        protocol="EMAIL",
    )

    executed = project_user_api_client.execute(
        ADD_MESSAGE_MUTATION, variables=variables
    )

    assert_match_error_code(executed, DATA_VALIDATION_ERROR)


@pytest.mark.django_db
def test_cannot_add_message_unauthorized(project, wrong_project_api_client):
    executed = wrong_project_api_client.execute(
        ADD_MESSAGE_MUTATION, variables=get_add_message_variables(project)
    )

    assert_permission_denied(executed)


UPDATE_MESSAGE_MUTATION = """
mutation UpdateMessage($input: UpdateMessageMutationInput!) {
  updateMessage(input: $input) {
    message {
      protocol
      translations {
        languageCode
        subject
        bodyText
      }
      sentAt
      recipientSelection
      recipientCount
      project {
        year
      }
      event {
        name
      }
      occurrences {
        edges {
          node {
            time
          }
        }
      }
    }
  }
}
"""


def get_update_message_variables(
    message, event=None, occurrences=None, recipient="ATTENDED", **kwargs
):
    variables = {
        "input": {
            "translations": [
                {
                    "subject": "Päivitetty testiotsikko",
                    "bodyText": "Päivitetty testiteksti.",
                    "languageCode": "FI",
                }
            ],
            "recipientSelection": recipient,
            "id": get_global_id(message),
            **kwargs,
        }
    }
    if event:
        variables["input"]["eventId"] = get_global_id(event)
    if occurrences is not None:
        variables["input"]["occurrenceIds"] = [get_global_id(o) for o in occurrences]
    return variables


@pytest.mark.parametrize("event_selection", (None, "event", "event_and_occurrences"))
@pytest.mark.django_db
def test_update_message(snapshot, project_user_api_client, event_selection):
    old_event = EventFactory(published_at=now())
    message = MessageFactory(event=old_event)
    old_occurrences = OccurrenceFactory.create_batch(2, event=message.event)
    message.occurrences.set(old_occurrences)

    if event_selection == "event":
        new_event = EventFactory(published_at=now())
        new_occurrences = []
    elif event_selection == "event_and_occurrences":
        new_event = EventFactory(published_at=now())
        new_occurrences = [
            OccurrenceFactory(
                event=new_event,
                time=datetime(2016, 8, 16, 7, 10, 0, tzinfo=now().tzinfo),
            )
        ]
    else:
        new_event = None
        new_occurrences = []

    variables = get_update_message_variables(
        message,
        event=new_event,
        occurrences=new_occurrences,
        protocol=Message.SMS.upper(),
    )

    executed = project_user_api_client.execute(
        UPDATE_MESSAGE_MUTATION, variables=variables
    )

    snapshot.assert_match(executed)
    message.refresh_from_db()
    assert message.subject == "Päivitetty testiotsikko"
    assert message.body_text == "Päivitetty testiteksti."
    assert message.event == (
        new_event
        if event_selection in ("event", "event_and_occurrences")
        else old_event
    )
    assert [o.pk for o in message.occurrences.all()] == [o.pk for o in new_occurrences]


@pytest.mark.parametrize("event_selection", ("event", "event_and_occurrences"))
@pytest.mark.django_db
def test_cannot_update_event_for_invited_group_message(
    project_user_api_client, message, event_selection
):
    event = EventFactory(published_at=now())
    occurrences = []

    if event_selection == "event_and_occurrences":
        occurrences = [OccurrenceFactory(event=event)]

    variables = get_update_message_variables(
        message, event=event, occurrences=occurrences, recipient="INVITED"
    )

    executed = project_user_api_client.execute(
        UPDATE_MESSAGE_MUTATION, variables=variables
    )

    assert_match_error_code(executed, DATA_VALIDATION_ERROR)


@pytest.mark.django_db
def test_cannot_update_message_unauthorized(message, wrong_project_api_client):
    executed = wrong_project_api_client.execute(
        UPDATE_MESSAGE_MUTATION,
        variables=get_update_message_variables(message),
    )

    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)


@pytest.mark.django_db
def test_cannot_update_sent_message(project_user_api_client, sent_message):
    executed = project_user_api_client.execute(
        UPDATE_MESSAGE_MUTATION,
        variables={"input": {"id": get_global_id(sent_message)}},
    )
    assert_match_error_code(executed, MESSAGE_ALREADY_SENT_ERROR)


SEND_MESSAGE_MUTATION = """
mutation SendMessage($input: SendMessageMutationInput!) {
  sendMessage(input: $input) {
    message {
      protocol
      subject
      sentAt
      recipientCount
    }
  }
}
"""


@pytest.mark.django_db
def test_send_message(snapshot, project_user_api_client, message):
    ChildWithGuardianFactory()

    executed = project_user_api_client.execute(
        SEND_MESSAGE_MUTATION, variables={"input": {"id": get_global_id(message)}}
    )

    snapshot.assert_match(executed)
    assert len(mail.outbox) == 1


@pytest.mark.django_db
@patch.object(SMSNotificationService, "send_sms")
def test_send_sms_message_sent_with_default_language(
    mock_send_sms, snapshot, project_user_api_client, sms_message
):
    child = ChildWithGuardianFactory(relationship__guardian__language="sv")
    guardian = child.relationships.first().guardian

    executed = project_user_api_client.execute(
        SEND_MESSAGE_MUTATION, variables={"input": {"id": get_global_id(sms_message)}}
    )
    assert guardian.language == "sv"
    assert executed["data"]["sendMessage"]["message"]["subject"] == "Otsikko"
    snapshot.assert_match(executed)
    assert len(mail.outbox) == 0
    mock_send_sms.assert_called_once()


@pytest.mark.django_db
def test_cannot_send_message_unauthorized(wrong_project_api_client, message):
    executed = wrong_project_api_client.execute(
        SEND_MESSAGE_MUTATION, variables={"input": {"id": get_global_id(message)}}
    )

    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)


@pytest.mark.django_db
def test_cannot_send_message_more_than_once(project_user_api_client, sent_message):
    ChildWithGuardianFactory()

    executed = project_user_api_client.execute(
        SEND_MESSAGE_MUTATION, variables={"input": {"id": get_global_id(sent_message)}}
    )

    assert_match_error_code(executed, MESSAGE_ALREADY_SENT_ERROR)
    assert len(mail.outbox) == 0


DELETE_MESSAGE_MUTATION = """
mutation DeleteMessage($input: DeleteMessageMutationInput!) {
   deleteMessage(input: $input) {
    clientMutationId
  }
}
"""


@pytest.mark.django_db
def test_delete_message(snapshot, project_user_api_client, message):
    executed = project_user_api_client.execute(
        DELETE_MESSAGE_MUTATION, variables={"input": {"id": get_global_id(message)}}
    )

    snapshot.assert_match(executed)
    assert Message.objects.count() == 0


@pytest.mark.django_db
def test_cannot_delete_message_unauthorized(wrong_project_api_client, message):
    executed = wrong_project_api_client.execute(
        DELETE_MESSAGE_MUTATION, variables={"input": {"id": get_global_id(message)}}
    )

    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)


@pytest.mark.django_db
def test_cannot_delete_sent_message(project_user_api_client, sent_message):
    executed = project_user_api_client.execute(
        DELETE_MESSAGE_MUTATION,
        variables={"input": {"id": get_global_id(sent_message)}},
    )

    assert_match_error_code(executed, MESSAGE_ALREADY_SENT_ERROR)
    assert Message.objects.count() == 1
