import factory
from django.conf import settings

from projects.models import Project
from venues.models import Venue


class VenueFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=64)
    description = factory.Faker("text")
    address = factory.Faker("address")
    accessibility_info = factory.Faker("text")
    arrival_instructions = factory.Faker("text")
    additional_info = factory.Faker("text")
    wc_and_facilities = factory.Faker("text")
    www_url = factory.Faker("url")
    is_system = False
    project = factory.LazyFunction(lambda: Project.objects.get(year=2020))

    class Meta:
        model = Venue
        skip_postgeneration_save = True  # Not needed after factory v4.0.0

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if kwargs.get("is_system"):
            existing = model_class.objects.filter(is_system=True).first()
            if existing:
                return existing
        return super()._create(model_class, *args, **kwargs)


class SystemVenueFactory(VenueFactory):
    is_system = True
    project = None
    name = factory.LazyFunction(lambda: settings.KUKKUU_DEFAULT_VENUE_NAME)
