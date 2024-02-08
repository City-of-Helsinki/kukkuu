from unittest.mock import patch

import pytest

from common.tests.conftest import create_api_client_with_user
from common.tests.utils import (
    assert_mails_match_snapshot,
    create_notification_template_in_language,
)
from users.factories import GuardianFactory
from users.notifications import NotificationType
from users.tests.mutations import REQUEST_EMAIL_CHANGE_TOKEN_MUTATION


@pytest.fixture
def notification_template_guardian_email_changed_fi():
    return create_notification_template_in_language(
        NotificationType.GUARDIAN_EMAIL_CHANGED,
        "fi",
        subject="Guardian email changed FI",
        body_text="Guardian FI: {{ guardian }}",
    )


@pytest.fixture
def notification_template_guardian_email_change_requested_fi():
    return create_notification_template_in_language(
        NotificationType.GUARDIAN_EMAIL_CHANGE_TOKEN,
        "fi",
        subject="Guardian email change verification token requested FI",
        body_text="Guardian FI: {{ guardian }}. Token: {{ verification_token }}",
    )


@pytest.mark.parametrize(
    "new_email", ("new.email@example.com", "old.email@example.com", None)
)
@pytest.mark.django_db
def test_guardian_changed_email_notification(
    snapshot, new_email, notification_template_guardian_email_changed_fi
):
    guardian = GuardianFactory(
        first_name="Black", last_name="Guardian", email="old.email@example.com"
    )
    api_client = create_api_client_with_user(guardian.user)
    params = {"email": new_email} if new_email else {}

    api_client.execute(
        """
    mutation UpdateMyProfile($input: UpdateMyProfileMutationInput!) {
      updateMyProfile(input: $input) {
        myProfile {
          email
        }
      }
    }
    """,
        variables={"input": {"firstName": "White", **params}},
    )

    assert_mails_match_snapshot(snapshot)


@patch("verification_tokens.models.VerificationToken.generate_key")
@pytest.mark.django_db
def test_guardian_change_email_token_requested_notification(
    mock_generate_key,
    snapshot,
    notification_template_guardian_email_change_requested_fi,
):
    # patch the return value for snapshot testing
    mock_generate_key.return_value = "abc123+-"
    email = "email@example.com"
    guardian = GuardianFactory(email=email)
    api_client = create_api_client_with_user(guardian.user)

    executed = api_client.execute(
        REQUEST_EMAIL_CHANGE_TOKEN_MUTATION,
        variables={},
    )

    assert (
        executed["data"]["requestEmailUpdateToken"]["emailUpdateTokenRequested"] is True
    )
    assert executed["data"]["requestEmailUpdateToken"]["email"] == email
    assert_mails_match_snapshot(snapshot)
