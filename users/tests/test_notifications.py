from unittest.mock import patch

import pytest
from django.core import mail

from children.factories import ChildWithGuardianFactory
from common.tests.conftest import create_api_client_with_user
from common.tests.utils import (
    assert_mails_match_snapshot,
    create_notification_template_in_language,
)
from events.factories import EnrolmentFactory
from users.factories import GuardianFactory
from users.notifications import NotificationType
from users.services import AuthServiceNotificationService
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
        body_text="Guardian FI: {{ guardian }}. Unsubscribe: {{unsubscribe_url}}",
    )


@pytest.fixture
def notification_template_guardian_email_change_requested_fi():
    return create_notification_template_in_language(
        NotificationType.GUARDIAN_EMAIL_CHANGE_TOKEN,
        "fi",
        subject="Guardian email change verification token requested FI",
        body_text="""Guardian FI: {{ guardian }}.
        Token: {{ verification_token }}.
        Unsubscribe: {{unsubscribe_url}}
        """,
    )


USER_AUTH_SERVICE_IS_CHANGING_TEMPLATE = """
Guardian FI: {{ guardian }}.
The change is happening {{ date_of_change_str|default('17.6.2024', true) }}.
{% if guardian.children.count() %}
Childrens' event participation history:

{% for child in guardian.children.all() %}
Child name: {{child.name}}

{% for enrolment in child.enrolments.all() %}
Event: {{enrolment.occurrence.event.name}}
Occurrence: {{enrolment.occurrence.time}}

{% endfor %}
{% endfor %}
{% endif %}
{% if children_event_history_markdown %}
Markdown: 
{{children_event_history_markdown}}
{% endif %}"""  # noqa W291


@pytest.fixture
def notification_template_user_auth_service_is_changing_fi():
    return create_notification_template_in_language(
        NotificationType.USER_AUTH_SERVICE_IS_CHANGING,
        "fi",
        subject="User authorization service is changing FI",
        body_text=USER_AUTH_SERVICE_IS_CHANGING_TEMPLATE,
    )


@pytest.mark.parametrize(
    "new_email", ("new.email@example.com", "old.email@example.com", None)
)
@pytest.mark.django_db
def test_guardian_changed_email_notification(
    snapshot,
    new_email,
    notification_template_guardian_email_changed_fi,
    mock_user_create_subscriptions_management_auth_token,
):
    old_email = "old.email@example.com"
    guardian = GuardianFactory(email=old_email)
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
    assert len(mail.outbox) == (1 if (new_email and new_email != old_email) else 0)
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
    mock_user_create_subscriptions_management_auth_token,
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
    assert len(mail.outbox) == (1 if new_email else 0)
    assert_mails_match_snapshot(snapshot)


@pytest.mark.django_db
def test_send_user_auth_service_is_changing_notifications(
    notification_template_user_auth_service_is_changing_fi,
):
    GuardianFactory.create_batch(3, user__is_obsolete=True)
    AuthServiceNotificationService.send_user_auth_service_is_changing_notifications()
    assert len(mail.outbox) == 3


@pytest.mark.django_db
@pytest.mark.parametrize("date_of_change_str", [None, "", "24.12.2024"])
def test_send_user_auth_service_is_changing_with_date_of_change_str_param(
    date_of_change_str, snapshot, notification_template_user_auth_service_is_changing_fi
):
    """if no date_of_change_str is given, the default should be used.
    The default is set in `notification_template_user_auth_service_is_changing_fi`:
    "The change is happening 17.6.2024".
    """
    GuardianFactory(user__is_obsolete=True)
    AuthServiceNotificationService.send_user_auth_service_is_changing_notifications(
        date_of_change_str=date_of_change_str
    )
    assert len(mail.outbox) == 1
    assert_mails_match_snapshot(snapshot)


@pytest.mark.django_db
def test_send_user_auth_service_is_changing_with_children(
    snapshot, notification_template_user_auth_service_is_changing_fi
):
    guardian = GuardianFactory(user__is_obsolete=True)
    children = ChildWithGuardianFactory.create_batch(2, relationship__guardian=guardian)
    for child in children:
        EnrolmentFactory.create_batch(2, child=child)
    AuthServiceNotificationService.send_user_auth_service_is_changing_notifications()
    assert len(mail.outbox) == 1
    assert_mails_match_snapshot(snapshot)
