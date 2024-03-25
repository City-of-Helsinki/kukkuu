import pytest
from django.contrib.auth import get_user_model

from children.factories import ChildFactory, ChildWithGuardianFactory
from children.models import Child
from subscriptions.factories import FreeSpotNotificationSubscriptionFactory
from subscriptions.models import FreeSpotNotificationSubscription
from users.models import Guardian
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
