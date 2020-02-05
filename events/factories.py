import factory
import pytz

from events.models import Event, Occurrence
from venues.factories import VenueFactory


class EventFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=64)
    duration = factory.Faker("random_int", max=300)
    short_description = factory.Faker("text", max_nb_chars=64)
    description = factory.Faker("text")
    image = factory.Faker("file_name", extension="jpg")
    participants_per_invite = factory.Faker(
        "random_element", elements=[x[0] for x in Event.PARTICIPANT_AMOUNT_CHOICES]
    )
    capacity_per_occurrence = factory.Faker("random_int", max=1000)

    class Meta:
        model = Event


class OccurrenceFactory(factory.django.DjangoModelFactory):
    time = factory.Faker("date_time", tzinfo=pytz.timezone("Europe/Helsinki"))
    event = factory.SubFactory(EventFactory)
    venue = factory.SubFactory(VenueFactory)

    class Meta:
        model = Occurrence
