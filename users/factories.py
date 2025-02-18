import uuid

import factory
from django.contrib.auth import get_user_model
from django.db.models import Q

from common.mixins import SaveAfterPostGenerationMixin
from languages.models import Language
from users.models import Guardian


class UserFactory(factory.django.DjangoModelFactory):
    """
    Testing, testing, don't merge this change
    """

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Faker("user_name")
    email = factory.Faker("email")

    class Meta:
        model = get_user_model()
        skip_postgeneration_save = True  # Not needed after factory v4.0.0


class GuardianFactory(SaveAfterPostGenerationMixin, factory.django.DjangoModelFactory):
    id = factory.LazyFunction(lambda: uuid.uuid4())
    user = factory.SubFactory(UserFactory)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Faker("phone_number")

    class Meta:
        model = Guardian

    @factory.post_generation
    def relationships(self, created, extracted, **kwargs):
        count = kwargs.pop("count", None)
        if count:
            from children.factories import RelationshipFactory

            RelationshipFactory.create_batch(count, guardian=self, **kwargs)

    @factory.post_generation
    def languages_spoken_at_home(self, created, extracted, **kwargs):
        if languages_spoken_at_home := extracted:
            filters = Q(alpha_3_code__in=languages_spoken_at_home)
            if None in languages_spoken_at_home:
                filters |= Q(alpha_3_code=None)
            self.languages_spoken_at_home.set(Language.objects.filter(filters))
