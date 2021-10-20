import pytest
from django.utils.timezone import now
from parler.utils.context import switch_language

from common.tests.conftest import *  # noqa
from messaging.factories import MessageFactory
from messaging.models import Message


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture
def message():
    message = MessageFactory(
        subject="Otsikko", body_text="Ruumisteksti.", recipient_selection=Message.ALL
    )
    with switch_language(message, "en"):
        message.subject = "Subject"
        message.body_text = "Body text."
        message.save()
    return message


@pytest.fixture
def sent_message():
    message = MessageFactory(
        subject="Lähetetty otsikko",
        body_text="Lähetetty ruumisteksti.",
        recipient_selection=Message.ALL,
        sent_at=now(),
    )
    with switch_language(message, "en"):
        message.subject = "Sent subject"
        message.body_text = "Sent body text."
        message.save()
    return message
