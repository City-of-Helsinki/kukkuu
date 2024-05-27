from copy import deepcopy

import pytest
from django.core import mail

from children.tests.mutations import SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION
from children.tests.test_api import SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES
from common.tests.utils import (
    assert_mails_match_snapshot,
    create_notification_template_in_language,
)
from users.factories import GuardianFactory

from ..notifications import NotificationType


@pytest.fixture
def notification_template_signup_fi():
    return create_notification_template_in_language(
        NotificationType.SIGNUP,
        "fi",
        subject="SIGNUP-notifikaation aihe",
        body_text="""
SIGNUP-notifikaation sisältö tekstimuodossa.
Lapset: {{ children }}
Huoltaja: {{ guardian }}
Unsubscribe: {{unsubscribe_url}}
""",
    )


@pytest.fixture
def notification_template_signup_en():
    return create_notification_template_in_language(
        NotificationType.SIGNUP,
        "en",
        subject="SIGNUP notification subject",
        body_text="""
SIGNUP notification body text.
Children: {{ children }}
Guardian: {{ guardian }}
Unsubscribe: {{unsubscribe_url}}
""",
    )


@pytest.mark.django_db
def test_signup_notification(
    snapshot,
    user_api_client,
    notification_template_signup_fi,
    mock_user_create_subscriptions_management_auth_token,
):
    user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION,
        variables=SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES,
    )

    assert_mails_match_snapshot(snapshot)


@pytest.mark.django_db
def test_signup_notification_guardian_exists(
    snapshot,
    user_api_client,
    notification_template_signup_fi,
    mock_user_create_subscriptions_management_auth_token,
):
    GuardianFactory(user=user_api_client.user)

    user_api_client.execute(
        SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION,
        variables=SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES,
    )

    assert len(mail.outbox) == 0


@pytest.mark.parametrize("language", ["FI", "EN", "SV"])
@pytest.mark.django_db
def test_signup_notification_language(
    snapshot,
    user_api_client,
    language,
    notification_template_signup_fi,
    notification_template_signup_en,
    mock_user_create_subscriptions_management_auth_token,
):
    variables = deepcopy(SUBMIT_CHILDREN_AND_GUARDIAN_VARIABLES)
    variables["input"]["guardian"]["language"] = language

    user_api_client.execute(SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION, variables=variables)

    # SV should be the same as FI as there are no SV translation
    assert_mails_match_snapshot(snapshot)
