import pytest
from django.contrib.auth import get_user_model

from children.factories import ChildFactory, ChildWithGuardianFactory
from children.models import Child
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
