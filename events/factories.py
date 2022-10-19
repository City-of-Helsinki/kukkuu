import factory
import pytz
from django.utils import timezone

from children.factories import ChildFactory
from events.models import Enrolment, Event, EventGroup, Occurrence, TicketSystemPassword
from projects.models import Project
from venues.factories import VenueFactory


class EventGroupFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=64)
    short_description = factory.Faker("text", max_nb_chars=64)
    description = factory.Faker("text")
    image = factory.Faker("file_name", extension="jpg")
    project = factory.LazyFunction(lambda: Project.objects.get(year=2020))

    class Meta:
        model = EventGroup


class EventFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=64)
    duration = factory.Faker("random_int", max=300)
    short_description = factory.Faker("text", max_nb_chars=64)
    description = factory.Faker("text")
    image = factory.Faker("file_name", extension="jpg")
    participants_per_invite = factory.Faker(
        "random_element", elements=[x[0] for x in Event.PARTICIPANTS_PER_INVITE_CHOICES]
    )
    capacity_per_occurrence = factory.Faker("random_int", max=50)
    project = factory.LazyFunction(lambda: Project.objects.get(year=2020))
    event_group = None
    ready_for_event_group_publishing = True

    class Meta:
        model = Event


class TicketmasterEventFactory(EventFactory):
    published_at = factory.LazyFunction(lambda: timezone.now())
    ticket_system = Event.TICKETMASTER
    ticket_system_url = factory.Faker("url")
    capacity_per_occurrence = None
    duration = None


class OccurrenceFactory(factory.django.DjangoModelFactory):
    time = factory.Faker("date_time", tzinfo=pytz.timezone("Europe/Helsinki"))
    event = factory.SubFactory(EventFactory)
    venue = factory.SubFactory(VenueFactory)

    class Meta:
        model = Occurrence

    @factory.post_generation
    def messages(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for message in extracted:
                self.messages.add(message)


class EnrolmentFactory(factory.django.DjangoModelFactory):
    child = factory.SubFactory("children.factories.ChildFactory")
    occurrence = factory.SubFactory(OccurrenceFactory)

    class Meta:
        model = Enrolment


class TicketSystemPasswordFactory(factory.django.DjangoModelFactory):
    value = factory.Faker("password")
    event = factory.SubFactory(EventFactory)
    child = factory.SubFactory(ChildFactory)

    class Meta:
        model = TicketSystemPassword
