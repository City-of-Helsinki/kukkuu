import factory

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
    project = factory.LazyFunction(lambda: Project.objects.get(year=2020))

    class Meta:
        model = Venue
        skip_postgeneration_save = True  # Not needed after factory v4.0.0
