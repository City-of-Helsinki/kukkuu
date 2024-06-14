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


@pytest.fixture(params=("-o", "--obsolete_handled_users"))
def obsolete_handled_users_argument(request):
    return request.param


@pytest.fixture(params=("-b", "--batch_size"))
def batch_size_argument(request):
    return request.param


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


@pytest.mark.django_db
def test_command_obsolete_handled_users_default():
    """
    Test that the handled users are not marked as obsolete by default.
    """
    GuardianFactory.create_batch(
        size=3,
        user__date_joined=timezone.now() - timedelta(days=1),
        user__is_obsolete=False,
    )
    assert Guardian.objects.count() == 3
    assert Guardian.objects.filter(user__is_obsolete=False).count() == 3

    with mock.patch.object(
        AuthServiceNotificationService,
        "_send_auth_service_is_changing_notification",
    ):
        call_command(
            "send_user_auth_service_is_changing_notifications",
            # Needed for including the non-obsoleted users as input:
            "--include_non_obsoleted",
        )

    # By default should not mark any users as obsolete
    assert Guardian.objects.filter(user__is_obsolete=True).count() == 0


@pytest.mark.django_db
def test_command_obsolete_handled_users_true(obsolete_handled_users_argument):
    """
    Test that "-o" or "--obsolete_handled_users" argument
    marks the handled users as obsolete.
    """
    GuardianFactory.create_batch(
        size=3,
        user__date_joined=timezone.now() - timedelta(days=1),
        user__is_obsolete=False,
    )
    assert Guardian.objects.count() == 3
    assert Guardian.objects.filter(user__is_obsolete=False).count() == 3

    with mock.patch.object(
        AuthServiceNotificationService,
        "_send_auth_service_is_changing_notification",
    ):
        call_command(
            "send_user_auth_service_is_changing_notifications",
            obsolete_handled_users_argument,
            # Needed for including the non-obsoleted users as input:
            "--include_non_obsoleted",
        )

    # Should mark all users as obsolete
    assert Guardian.objects.filter(user__is_obsolete=True).count() == 3


@pytest.mark.parametrize(
    "guardian_count,batch_size_value,expected_num_queries",
    [
        (
            guardian_count,
            batch_size_value,
            (guardian_count // batch_size_value)  # Full batches count
            + (
                0 if (guardian_count % batch_size_value) == 0 else 1
            )  # Partial last batch if not divisible by batch size
            + 1  # Guardian query
            + 1,  # Children prefetch query
        )
        for guardian_count in [1, 60]
        for batch_size_value in [1, 3, 10, 11, 25, 60, 1000, 1000000]
    ],
)
@pytest.mark.django_db
def test_command_obsolete_handled_users_with_batch_size(
    django_assert_num_queries,
    obsolete_handled_users_argument,
    batch_size_argument,
    guardian_count,
    batch_size_value,
    expected_num_queries,
):
    """
    Test that "-o" or "--obsolete_handled_users" argument
    marks the handled users as obsolete with different batch sizes.
    """
    GuardianFactory.create_batch(
        size=guardian_count,
        user__date_joined=timezone.now() - timedelta(days=1),
        user__is_obsolete=False,
    )
    assert Guardian.objects.count() == guardian_count
    assert Guardian.objects.filter(user__is_obsolete=False).count() == guardian_count

    with mock.patch.object(
        AuthServiceNotificationService,
        "_send_auth_service_is_changing_notification",
    ):
        with django_assert_num_queries(expected_num_queries):
            call_command(
                "send_user_auth_service_is_changing_notifications",
                batch_size_argument,
                str(batch_size_value),
                obsolete_handled_users_argument,
                # Needed for including the non-obsoleted users as input:
                "--include_non_obsoleted",
            )

    # Should mark all users as obsolete
    assert Guardian.objects.filter(user__is_obsolete=True).count() == guardian_count


@pytest.mark.parametrize("batch_size_value", [0, -1, -9999])
@pytest.mark.django_db
def test_command_invalid_batch_size(batch_size_argument, batch_size_value):
    with pytest.raises(CommandError) as excinfo:
        with mock.patch.object(
            AuthServiceNotificationService,
            "_send_auth_service_is_changing_notification",
        ):
            call_command(
                "send_user_auth_service_is_changing_notifications",
                batch_size_argument,
                str(batch_size_value),
            )
        assert "--batch_size must be at least 1" in str(excinfo.value)
