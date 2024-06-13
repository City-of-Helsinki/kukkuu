from datetime import timedelta
from unittest import mock

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from users.factories import GuardianFactory
from users.models import Guardian
from users.services import AuthServiceNotificationService


@mock.patch.object(
    Guardian.objects,
    "for_auth_service_is_changing_notification",
    return_value=Guardian.objects.none(),
)
@mock.patch.object(
    AuthServiceNotificationService,
    "send_user_auth_service_is_changing_notifications",
)
@pytest.mark.django_db
def test_command_no_filters(mock_notification_service, mock_guardian_queryset):
    # Test the command without any filters
    call_command("send_user_auth_service_is_changing_notifications")

    mock_guardian_queryset.assert_called_once_with(
        user_joined_before=None, obsoleted_users_only=True, guardian_emails=None
    )
    mock_notification_service.assert_called_once()  # Called with the empty queryset


@mock.patch.object(
    Guardian.objects,
    "for_auth_service_is_changing_notification",
    return_value=Guardian.objects.none(),
)
@mock.patch.object(
    AuthServiceNotificationService,
    "send_user_auth_service_is_changing_notifications",
)
@pytest.mark.django_db
def test_command_joined_before_filter(
    mock_notification_service, mock_guardian_queryset
):
    # Test the joined_before filter
    input = timezone.now().isoformat()
    call_command("send_user_auth_service_is_changing_notifications", "-j", input)

    mock_guardian_queryset.assert_called_once_with(
        user_joined_before=parse_datetime(input),
        obsoleted_users_only=True,
        guardian_emails=None,
    )
    mock_notification_service.assert_called_once()


@mock.patch.object(
    Guardian.objects,
    "for_auth_service_is_changing_notification",
    return_value=Guardian.objects.none(),
)
@mock.patch.object(
    AuthServiceNotificationService,
    "send_user_auth_service_is_changing_notifications",
)
@pytest.mark.django_db
def test_command_include_non_obsoleted(
    mock_notification_service, mock_guardian_queryset
):
    # Test including non-obsoleted users
    call_command(
        "send_user_auth_service_is_changing_notifications", "--include_non_obsoleted"
    )

    mock_guardian_queryset.assert_called_once_with(
        user_joined_before=None, obsoleted_users_only=False, guardian_emails=None
    )
    mock_notification_service.assert_called_once()


@pytest.mark.django_db
def test_invalid_date_format():
    # Test handling of invalid date format
    with pytest.raises(CommandError) as excinfo:
        call_command(
            "send_user_auth_service_is_changing_notifications", "-j", "invalid-datetime"
        )
    assert "Invalid datetime format" in str(excinfo.value)


@mock.patch.object(
    Guardian.objects,
    "for_auth_service_is_changing_notification",
    return_value=Guardian.objects.none(),
)
@mock.patch.object(
    AuthServiceNotificationService,
    "send_user_auth_service_is_changing_notifications",
)
@pytest.mark.django_db
def test_command_with_emails_filter(mock_notification_service, mock_guardian_queryset):
    # Test including non-obsoleted users
    call_command(
        "send_user_auth_service_is_changing_notifications",
        "-e",
        "test@example.com",
        "another@test.com",
    )

    mock_guardian_queryset.assert_called_once_with(
        user_joined_before=None,
        obsoleted_users_only=True,
        guardian_emails=["test@example.com", "another@test.com"],
    )
    mock_notification_service.assert_called_once()


@pytest.mark.parametrize(
    "max_guardian_count,expected_sent_count",
    [
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 3),
        (9999, 3),
    ],
)
@pytest.mark.django_db
def test_command_max_guardian_count_filter(
    capfd,
    max_guardian_count,
    expected_sent_count,
):
    GuardianFactory.create_batch(
        size=3,
        user__date_joined=timezone.now() - timedelta(days=1),
        user__is_obsolete=True,
    )
    assert Guardian.objects.count() == 3
    assert Guardian.objects.filter(user__is_obsolete=True).count() == 3

    with mock.patch.object(
        AuthServiceNotificationService,
        "send_user_auth_service_is_changing_notifications",
    ):
        call_command(
            "send_user_auth_service_is_changing_notifications",
            "-m",
            str(max_guardian_count),
        )

    captured = capfd.readouterr()
    assert (
        f"Sent {expected_sent_count} user auth service is changing notifications."
        in captured.out
    )
