import factory.django
import pytz
from django.contrib.contenttypes.models import ContentType

from users.factories import UserFactory

from .models import VerificationToken


class VerificationTokenFactory(factory.django.DjangoModelFactory):
    object_id = factory.SelfAttribute("content_object.id")
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )
    user = factory.SubFactory(UserFactory)
    key = VerificationToken.generate_key()
    expiry_date = factory.Faker(
        "future_datetime", end_date="+15m", tzinfo=pytz.timezone("Europe/Helsinki")
    )
    is_active = True

    class Meta:
        model = VerificationToken
        exclude = ["content_object"]
        abstract = True


class UserEmailVerificationTokenFactory(VerificationTokenFactory):
    content_object = factory.LazyAttribute(lambda o: o.user)
    verification_type = VerificationToken.VERIFICATION_TYPE_EMAIL_VERIFICATION


class UserSubscriptionsAuthVerificationTokenFactory(VerificationTokenFactory):
    content_object = factory.LazyAttribute(lambda o: o.user)
    verification_type = VerificationToken.VERIFICATION_TYPE_SUBSCRIPTIONS_AUTH
