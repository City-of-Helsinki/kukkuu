import factory

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

    class Meta:
        model = Venue
