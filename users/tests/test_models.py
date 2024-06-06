from datetime import timedelta
from uuid import UUID

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from freezegun import freeze_time

from children.factories import ChildFactory, ChildWithGuardianFactory
from children.models import Child
from children.notifications import NotificationType as ChildrenNotificationType
from events.consts import NotificationType as EventNotificationType
from events.factories import EnrolmentFactory, TicketSystemPasswordFactory
from gdpr.consts import CLEARED_VALUE
from subscriptions.factories import FreeSpotNotificationSubscriptionFactory
from subscriptions.models import FreeSpotNotificationSubscription
from subscriptions.notifications import (
    NotificationType as SubscriptionsNotificationType,
)
from users.models import Guardian
from users.notifications import NotificationType as UserNotificationType
from verification_tokens.factories import UserEmailVerificationTokenFactory
from verification_tokens.models import VerificationToken

from ..factories import GuardianFactory, UserFactory

User = get_user_model()


@pytest.mark.django_db
def test_user_creation():
    UserFactory()
    assert User.objects.count() == 1
    assert Child.objects.count() == 0


@pytest.mark.django_db
def test_guardian_creation():
    GuardianFactory()
    assert User.objects.count() == 1
    assert Child.objects.count() == 0
    assert Guardian.objects.count() == 1


@pytest.mark.django_db
def test_guardian_needs_to_accept_communication_explicitly():
    guardian = Guardian()
    assert not guardian.has_accepted_communication
    guardian = GuardianFactory()
    assert not guardian.has_accepted_communication
    guardian = GuardianFactory(has_accepted_communication=True)
    assert guardian.has_accepted_communication


@pytest.mark.django_db
def test_guardian_with_children_creation(project):
    GuardianFactory(relationships__count=3, relationships__child__project=project)
    assert Guardian.objects.count() == 1
    assert Child.objects.count() == 3
    assert list(Guardian.objects.first().children.all()) == list(Child.objects.all())


@pytest.mark.django_db
def test_guardian_email_populating():
    user = UserFactory(email="user@example.com")

    guardian = Guardian.objects.create(user=user)
    assert guardian.email == "user@example.com"

    guardian.email = "guardian@example.com"
    guardian.save()
    guardian.refresh_from_db()
    assert guardian.email == "guardian@example.com"

    guardian.email = ""
    guardian.save()
    guardian.refresh_from_db()
    assert guardian.email == "user@example.com"


@pytest.mark.parametrize("test_queryset", (False, True))
@pytest.mark.django_db
def test_children_deleted_when_guardian_deleted(test_queryset):
    child = ChildWithGuardianFactory()
    guardian = child.guardians.first()
    child_having_also_another_guardian = ChildFactory()
    child_having_also_another_guardian.guardians.set([guardian, GuardianFactory()])
    outsider = ChildWithGuardianFactory()

    if test_queryset:
        Guardian.objects.filter(id=guardian.id).delete()
    else:
        guardian.delete()

    with pytest.raises(Child.DoesNotExist):
        child.refresh_from_db()

    child_having_also_another_guardian.refresh_from_db()
    outsider.refresh_from_db()


@pytest.mark.django_db
def test_get_active_verification_tokens():
    UserEmailVerificationTokenFactory.create_batch(10)
    verification_token = UserEmailVerificationTokenFactory(
        is_active=True,
        verification_type=VerificationToken.VERIFICATION_TYPE_EMAIL_VERIFICATION,
    )
    user = verification_token.user
    UserEmailVerificationTokenFactory.create_batch(
        2,
        user=user,
        is_active=False,
    )
    assert VerificationToken.objects.count() == 13
    assert VerificationToken.objects.filter(user=user).count() == 3
    assert (
        list(user.get_active_verification_tokens())
        == list(
            user.get_active_verification_tokens(
                verification_type=VerificationToken.VERIFICATION_TYPE_EMAIL_VERIFICATION
            )
        )
        == [verification_token]
    )


@pytest.mark.django_db
def test_get_subscriptions():
    child = ChildWithGuardianFactory()
    guardian = child.guardians.first()
    user = guardian.user

    user_child_subscriptions = list(
        FreeSpotNotificationSubscriptionFactory.create_batch(5, child=child)
    )
    users_other_subscriptions = list(
        FreeSpotNotificationSubscriptionFactory.create_batch(5)
    )
    for subscription in users_other_subscriptions:
        subscription.child.guardians.set([guardian])
    users_subscriptions = user_child_subscriptions + users_other_subscriptions

    # Other users subscriptions in database
    FreeSpotNotificationSubscriptionFactory.create_batch(10)

    # when user_subscriptions is called without args
    results_without_args = user.get_subscriptions()
    # then it should match with the list of user's all subscriptions,
    # no matter the child
    assert len(users_subscriptions) == len(results_without_args) == 10
    assert all(s in results_without_args for s in users_subscriptions)

    # when user_subscriptions is called with child arg
    results_with_child_arg = user.get_subscriptions(child)
    # then it should match with the list of user's subscriptions for the child
    assert len(results_with_child_arg) == len(user_child_subscriptions) == 5
    assert all(s in results_with_child_arg for s in user_child_subscriptions)


@pytest.mark.django_db
def test_unsubscribe_all_notification_subscriptions():
    child = ChildWithGuardianFactory()
    guardian = child.guardians.first()
    user = guardian.user
    FreeSpotNotificationSubscriptionFactory.create_batch(5, child=child)
    users_other_subscriptions = list(
        FreeSpotNotificationSubscriptionFactory.create_batch(10)
    )
    for subscription in users_other_subscriptions:
        subscription.child.guardians.set([guardian])
    # when unsubscribe_all_notification_subscriptions with a child arg is called
    user.unsubscribe_all_notification_subscriptions(child=child)
    # then the users subscriptions related to a child should all be removed
    current_subscriptions = list(
        FreeSpotNotificationSubscription.objects.filter(child__guardians__user=user)
    )
    assert len(current_subscriptions) == len(users_other_subscriptions) == 10
    assert all(s in current_subscriptions for s in users_other_subscriptions)
    # when unsubscribe_all_notification_subscriptions without args is called
    user.unsubscribe_all_notification_subscriptions()
    # then all the users subscriptions should be removed
    assert (
        FreeSpotNotificationSubscription.objects.filter(
            child__guardians__user=user
        ).count()
        == 0
    )


@pytest.mark.django_db
def test_create_subscriptions_management_auth_token(user):
    assert VerificationToken.objects.filter(user=user).count() == 0
    user.create_subscriptions_management_auth_token()
    assert VerificationToken.objects.filter(user=user).count() == 1
    token = VerificationToken.objects.first()
    assert token.user == user
    assert token.content_object == user
    assert (
        token.verification_type
        == VerificationToken.VERIFICATION_TYPE_SUBSCRIPTIONS_AUTH
    )
    assert token.email == user.email
    assert token.expiry_date is not None
    assert len(token.key) >= 16  # the bare minimum for security reasons


@pytest.mark.django_db
def test_user_clear_gdpr_sensitive_data_fields():
    original_password = "readabletestpassword"
    user = UserFactory(password=original_password)
    assert user.first_name != ""
    assert user.last_name != ""
    assert user.email != ""
    assert user.password == original_password
    user.clear_gdpr_sensitive_data_fields()
    user.refresh_from_db()
    assert user.first_name == ""
    assert user.last_name == ""
    assert user.email == ""
    assert user.username == f"{CLEARED_VALUE}-{user.uuid}"
    assert user.is_active is False
    assert user.password != original_password


@pytest.mark.django_db
@pytest.mark.parametrize("user_email", ["user@kukkuu.hel.fi", ""])
def test_guardian_clear_gdpr_sensitive_data_fields(user_email):
    guardian_email = "guardian@kukkuu.hel.fi"
    guardian = GuardianFactory(email=guardian_email, user__email=user_email)
    assert guardian.email == guardian_email
    assert guardian.phone_number != ""
    guardian.clear_gdpr_sensitive_data_fields()
    guardian.refresh_from_db()
    assert guardian.first_name == CLEARED_VALUE
    assert guardian.last_name == CLEARED_VALUE
    assert guardian.email == guardian.user.email
    assert guardian.phone_number == ""


@pytest.mark.django_db
@freeze_time("2020-11-11 12:00:00")
def test_user_serialize(snapshot, project):
    guardian = GuardianFactory(
        id=UUID("8dff3da4-a329-4b81-971a-bc509df679b1"),
        user__uuid=UUID("fa354000-3c0c-11eb-86c5-acde48001122"),
    )
    user = guardian.user
    user.administered_projects = [project]
    user.save()
    [
        child_with_many_enrolments,
        child_with_one_enrolment,
        child_without_enrolments,
    ] = ChildWithGuardianFactory.create_batch(3, relationship__guardian=guardian)
    FreeSpotNotificationSubscriptionFactory(child=child_without_enrolments)
    FreeSpotNotificationSubscriptionFactory(child=child_with_one_enrolment)
    EnrolmentFactory.create_batch(5, child=child_with_many_enrolments)
    TicketSystemPasswordFactory.create_batch(5, child=child_with_many_enrolments)
    EnrolmentFactory(child=child_with_one_enrolment)
    TicketSystemPasswordFactory(child=child_with_one_enrolment)
    assert child_without_enrolments.enrolments.count() == 0
    assert child_without_enrolments.ticket_system_passwords.count() == 0
    user.refresh_from_db()
    snapshot.assert_match(user.serialize())


@pytest.mark.django_db
@pytest.mark.parametrize(
    "notification_type",
    [
        EventNotificationType.OCCURRENCE_ENROLMENT,
        EventNotificationType.OCCURRENCE_UNENROLMENT,
        EventNotificationType.OCCURRENCE_CANCELLED,
        EventNotificationType.OCCURRENCE_REMINDER,
        EventNotificationType.OCCURRENCE_FEEDBACK,
        ChildrenNotificationType.SIGNUP,
        UserNotificationType.GUARDIAN_EMAIL_CHANGE_TOKEN,
        UserNotificationType.GUARDIAN_EMAIL_CHANGED,
        SubscriptionsNotificationType.FREE_SPOT,
    ],
)
def test_has_accepted_communication_for_notification_irrefusables(notification_type):
    """Some of the notification types do not need an acceptance for communication.
    They are so called transactional notifications which cannot be rejected.
    Test that the GuardianQuerySet.has_accepted_communication_for_notification,
    does not check the acceptance for the types that don't need it.

    Args:
        notification_type (str): notification type
    """
    guardian_with_filtered_communication = GuardianFactory(
        has_accepted_communication=False
    )
    guardian_with_all_communication = GuardianFactory(has_accepted_communication=True)

    queryset_result = list(
        Guardian.objects.has_accepted_communication_for_notification(notification_type)
    )

    assert len(queryset_result) == 2
    assert guardian_with_all_communication in queryset_result
    assert guardian_with_filtered_communication in queryset_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "notification_type",
    [
        EventNotificationType.EVENT_PUBLISHED,
        EventNotificationType.EVENT_GROUP_PUBLISHED,
    ],
)
def test_has_accepted_communication_for_notification_needs_acceptance(
    notification_type,
):
    """Some of the notification types need an acceptance for communication.
    Test that the GuardianQuerySet.has_accepted_communication_for_notification,
    checks the acceptance for the types that need it.

    Args:
        notification_type (str): notification type
    """
    guardian_with_filtered_communication = GuardianFactory(
        has_accepted_communication=False
    )
    guardian_with_all_communication = GuardianFactory(has_accepted_communication=True)

    queryset_result = list(
        Guardian.objects.has_accepted_communication_for_notification(notification_type)
    )

    assert len(queryset_result) == 1
    assert guardian_with_all_communication in queryset_result
    assert guardian_with_filtered_communication not in queryset_result


@pytest.mark.django_db
@pytest.fixture
def obsoleted_guardian_joined_yesterday():
    return GuardianFactory(
        user__date_joined=timezone.now() - timedelta(days=1), user__is_obsolete=True
    )


@pytest.mark.django_db
@pytest.fixture
def guardian_joined_yesterday():
    return GuardianFactory(
        user__date_joined=timezone.now() - timedelta(days=1), user__is_obsolete=False
    )


@pytest.mark.django_db
@pytest.fixture
def guardian_joined_today():
    return GuardianFactory(user__date_joined=timezone.now(), user__is_obsolete=False)


@pytest.mark.django_db
def test_for_auth_service_is_changing_notification_default(
    obsoleted_guardian_joined_yesterday,
    guardian_joined_yesterday,
    guardian_joined_today,
):
    """Test with default parameters
    (no user_joined_before, obsoleted_users_only=True)
    """
    guardians = Guardian.objects.for_auth_service_is_changing_notification()
    assert obsoleted_guardian_joined_yesterday in guardians
    assert guardian_joined_yesterday in guardians  # Not obsoleted
    assert guardian_joined_today not in guardians  # Not obsoleted


@pytest.mark.django_db
@pytest.mark.parametrize("obsoleted_users_only", [True, False])
def test_for_auth_service_is_changing_notification_with_user_joined_before(
    obsoleted_users_only,
    obsoleted_guardian_joined_yesterday,
    guardian_joined_yesterday,
    guardian_joined_today,
):
    """Test with a specific user_joined_before date"""
    yesterday = timezone.now() - timedelta(days=1)
    guardians = Guardian.objects.for_auth_service_is_changing_notification(
        user_joined_before=yesterday, obsoleted_users_only=obsoleted_users_only
    )
    if not obsoleted_users_only:
        assert guardian_joined_yesterday in guardians
    assert obsoleted_guardian_joined_yesterday in guardians
    assert guardian_joined_today not in guardians


@pytest.mark.django_db
def test_for_auth_service_is_changing_notification_with_future_date():
    """Test with a future user_joined_before date (should raise ValueError)"""
    tomorrow = timezone.now() + timedelta(days=1)
    with pytest.raises(ValueError):
        Guardian.objects.for_auth_service_is_changing_notification(
            user_joined_before=tomorrow
        )


@pytest.mark.django_db
def test_for_auth_service_is_changing_notification_all_users(
    obsoleted_guardian_joined_yesterday,
    guardian_joined_yesterday,
    guardian_joined_today,
):
    """Test with obsoleted_users_only=False (should return all guardians)"""
    guardians = Guardian.objects.for_auth_service_is_changing_notification(
        obsoleted_users_only=False
    )
    assert obsoleted_guardian_joined_yesterday in guardians
    assert guardian_joined_yesterday in guardians
    assert guardian_joined_today in guardians
