from datetime import datetime

import pytest
from django.core import mail
from django.utils.timezone import now
from guardian.shortcuts import assign_perm
from messaging.factories import MessageFactory
from messaging.models import Message

from children.factories import ChildWithGuardianFactory
from common.tests.utils import assert_match_error_code, assert_permission_denied
from common.utils import get_global_id
from events.factories import EventFactory, OccurrenceFactory
from kukkuu.consts import MESSAGE_ALREADY_SENT_ERROR, OBJECT_DOES_NOT_EXIST_ERROR

MESSAGES_QUERY = """
query Messages {
  messages {
    edges {
      node {
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
  }
}
"""


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


def get_add_message_variables(project, event=None, occurrences=None):
    variables = {
        "input": {
            "translations": [
                {
                    "subject": "Testiotsikko",
                    "bodyText": "Testiteksti",
                    "languageCode": "FI",
                }
            ],
            "recipientSelection": "ALL",
            "projectId": get_global_id(project),
        }
    }
    if event:
        variables["input"]["eventId"] = get_global_id(event)
    if occurrences is not None:
        variables["input"]["occurrenceIds"] = [get_global_id(o) for o in occurrences]
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


def get_update_message_variables(message, event=None, occurrences=None):
    variables = {
        "input": {
            "translations": [
                {
                    "subject": "Päivitetty testiotsikko",
                    "bodyText": "Päivitetty testiteksti.",
                    "languageCode": "FI",
                }
            ],
            "recipientSelection": "ATTENDED",
            "id": get_global_id(message),
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
        message, event=new_event, occurrences=new_occurrences
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


@pytest.mark.django_db
def test_cannot_update_message_unauthorized(message, wrong_project_api_client):
    executed = wrong_project_api_client.execute(
        UPDATE_MESSAGE_MUTATION, variables=get_update_message_variables(message),
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
