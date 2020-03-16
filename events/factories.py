import factory
import pytz

from children.factories import ChildFactory
from events.models import Enrolment, Event, Occurrence
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
    capacity_per_occurrence = factory.Faker("random_int", max=50)

    class Meta:
        model = Event


class OccurrenceFactory(factory.django.DjangoModelFactory):
    time = factory.Faker("date_time", tzinfo=pytz.timezone("Europe/Helsinki"))
    event = factory.SubFactory(EventFactory)
    venue = factory.SubFactory(VenueFactory)

    class Meta:
        model = Occurrence


class EnrolmentFactory(factory.django.DjangoModelFactory):
    child = factory.SubFactory(ChildFactory)
    occurrence = factory.SubFactory(OccurrenceFactory)

    class Meta:
        model = Enrolment
