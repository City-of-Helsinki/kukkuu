from unittest.mock import patch

import pytest

from common.tests.conftest import create_api_client_with_user
from common.tests.utils import (
    assert_mails_match_snapshot,
    create_notification_template_in_language,
)
from users.factories import GuardianFactory
from users.notifications import NotificationType
from users.tests.mutations import (
    REQUEST_EMAIL_CHANGE_TOKEN_MUTATION,
    UPDATE_MY_EMAIL_MUTATION,
)
from verification_tokens.factories import UserEmailVerificationTokenFactory


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
    guardian = GuardianFactory(email="old.email@example.com")
    verification_token = UserEmailVerificationTokenFactory(
        user=guardian.user, email=new_email
    )
    api_client = create_api_client_with_user(guardian.user)
    api_client.execute(
        UPDATE_MY_EMAIL_MUTATION,
        variables={
            "input": {"email": new_email, "verificationToken": verification_token.key}
        },
    )

    assert_mails_match_snapshot(snapshot)


@patch("verification_tokens.models.VerificationToken.generate_key")
@pytest.mark.parametrize(
    "new_email", ("new.email@example.com", "old.email@example.com", None)
)
@pytest.mark.django_db
def test_guardian_change_email_token_requested_notification(
    mock_generate_key,
    new_email,
    snapshot,
    notification_template_guardian_email_change_requested_fi,
):
    # patch the return value for snapshot testing
    mock_generate_key.return_value = "abc123+-"
    old_email = "old.email@example.com"
    guardian = GuardianFactory(email=old_email)
    api_client = create_api_client_with_user(guardian.user)

    executed = api_client.execute(
        REQUEST_EMAIL_CHANGE_TOKEN_MUTATION,
        variables={"input": {"email": new_email}},
    )

    if new_email and new_email != old_email:
        assert (
            executed["data"]["requestEmailUpdateToken"]["emailUpdateTokenRequested"]
            is True
        )
        assert executed["data"]["requestEmailUpdateToken"]["email"] == new_email
    assert_mails_match_snapshot(snapshot)
