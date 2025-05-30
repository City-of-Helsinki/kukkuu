from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from users.factories import UserFactory
from verification_tokens.factories import (
    UserEmailVerificationTokenFactory,
    UserSubscriptionsAuthVerificationTokenFactory,
)
from verification_tokens.models import VerificationToken

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "model_factory",
    [UserEmailVerificationTokenFactory, UserSubscriptionsAuthVerificationTokenFactory],
)
def test_verification_token_creation(model_factory):
    verification_token = model_factory()
    assert VerificationToken.objects.count() == 1
    assert verification_token.content_object.__class__ == User
    assert verification_token.key is not None


@pytest.mark.django_db
def test_verification_token_is_valid():
    valid_token = UserEmailVerificationTokenFactory(
        expiry_date=timezone.now() + timedelta(minutes=10)
    )
    invalid_token1 = UserEmailVerificationTokenFactory(
        expiry_date=timezone.now() - timedelta(minutes=10)
    )
    invalid_token2 = UserEmailVerificationTokenFactory(is_active=False)
    assert valid_token.is_valid() is True
    assert invalid_token1.is_valid() is False
    assert invalid_token2.is_valid() is False


@pytest.mark.django_db
def test_verification_token_filter_active_tokens():
    token1 = UserEmailVerificationTokenFactory(is_active=False)
    token2 = UserEmailVerificationTokenFactory(is_active=True)
    token3 = UserEmailVerificationTokenFactory(is_active=True, key="123")
    # Test active with a class
    assert all(
        token in [token2, token3]
        for token in VerificationToken.objects.filter_active_tokens(User)
    )
    # Test active with an instance
    assert token2 in VerificationToken.objects.filter_active_tokens(
        token2.content_object
    )
    # Test inactive with an instance
    assert (
        len(VerificationToken.objects.filter_active_tokens(token1.content_object)) == 0
    )
    # Test active with a class and key
    assert (
        len(
            [
                t.id
                for t in VerificationToken.objects.filter_active_tokens(User, key="123")
            ]
        )
        == 1
    )
    # Test with a user
    assert (
        len(
            VerificationToken.objects.filter_active_tokens(
                token2.content_object, user=token2.user
            )
        )
        == 1
    )


@pytest.mark.django_db
def test_verification_token_deactivation():
    # Test with instance
    token1 = UserEmailVerificationTokenFactory(is_active=True)
    VerificationToken.objects.deactivate_token(token1.content_object)
    token1 = VerificationToken.objects.get(pk=token1.id)
    assert token1.is_active is False

    # test with class and key
    token2 = UserEmailVerificationTokenFactory(is_active=True)
    VerificationToken.objects.deactivate_token(User, key=token2.key)
    token2 = VerificationToken.objects.get(pk=token2.id)
    assert token2.is_active is False

    # Test with user
    token3 = UserEmailVerificationTokenFactory(is_active=True)
    VerificationToken.objects.deactivate_token(token3.content_object, user=token3.user)
    token3 = VerificationToken.objects.get(pk=token3.id)
    assert token3.is_active is False

    # Test with wrong user
    token4 = UserEmailVerificationTokenFactory(is_active=True)
    VerificationToken.objects.deactivate_token(token4.content_object, user=token3.user)
    token4 = VerificationToken.objects.get(pk=token4.id)
    assert token4.is_active is True

    # Test with verification_type
    token5 = UserEmailVerificationTokenFactory(is_active=True)
    VerificationToken.objects.deactivate_token(
        token5.content_object,
        verification_type=token5.verification_type,
        user=token5.user,
    )
    token5 = VerificationToken.objects.get(pk=token5.id)
    assert token5.is_active is False


@pytest.mark.django_db
def test_verification_token_create_token_with_manager():
    user = UserFactory()
    email = "adsf@asdf.com"

    token1 = VerificationToken.objects.create_token(
        user, user, VerificationToken.VERIFICATION_TYPE_EMAIL_VERIFICATION
    )
    assert token1.key is not None
    assert token1.content_object == user
    assert token1.user == user
    assert (
        token1.verification_type
        == VerificationToken.VERIFICATION_TYPE_EMAIL_VERIFICATION
    )
    assert token1.email == user.email

    token2 = VerificationToken.objects.create_token(
        user,
        user,
        VerificationToken.VERIFICATION_TYPE_EMAIL_VERIFICATION,
        email=email,
    )
    assert token2.email == email


@pytest.mark.django_db
def test_verification_token_deactivate_and_create_token():
    user = UserFactory()
    token1 = VerificationToken.objects.create_token(
        user, user, VerificationToken.VERIFICATION_TYPE_EMAIL_VERIFICATION
    )
    assert VerificationToken.objects.get(pk=token1.pk).is_active is True
    token2 = VerificationToken.objects.deactivate_and_create_token(
        user, user, VerificationToken.VERIFICATION_TYPE_EMAIL_VERIFICATION
    )
    assert VerificationToken.objects.get(pk=token1.pk).is_active is False
    assert VerificationToken.objects.get(pk=token2.pk).is_active is True


@pytest.mark.django_db
def test_clean_invalid_tokens_defaults():
    UserEmailVerificationTokenFactory(is_active=True)
    UserEmailVerificationTokenFactory(is_active=False)
    UserEmailVerificationTokenFactory(
        expiry_date=timezone.now() - timedelta(minutes=10)
    )
    assert VerificationToken.objects.count() == 3
    VerificationToken.objects.clean_invalid_tokens()
    assert VerificationToken.objects.count() == 1


@pytest.mark.django_db
def test_clean_invalid_tokens_inactive():
    UserEmailVerificationTokenFactory(is_active=True)
    UserEmailVerificationTokenFactory(is_active=False)
    expired_token = UserEmailVerificationTokenFactory(
        expiry_date=timezone.now() - timedelta(minutes=10)
    )
    assert VerificationToken.objects.count() == 3
    VerificationToken.objects.clean_invalid_tokens(
        clean_inactive=True, clean_expired=False
    )
    assert VerificationToken.objects.count() == 2
    assert VerificationToken.objects.filter(pk=expired_token.pk).exists()


@pytest.mark.django_db
def test_clean_invalid_tokens_expired():
    UserEmailVerificationTokenFactory(is_active=True)
    inactive_token = UserEmailVerificationTokenFactory(is_active=False)
    UserEmailVerificationTokenFactory(
        expiry_date=timezone.now() - timedelta(minutes=10)
    )
    assert VerificationToken.objects.count() == 3
    VerificationToken.objects.clean_invalid_tokens(
        clean_inactive=False, clean_expired=True
    )
    assert VerificationToken.objects.count() == 2
    assert VerificationToken.objects.filter(pk=inactive_token.pk).exists()
