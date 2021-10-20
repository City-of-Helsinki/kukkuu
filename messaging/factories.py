import factory

from projects.models import Project

from .models import Message


class MessageFactory(factory.django.DjangoModelFactory):
    subject = factory.Faker("text", max_nb_chars=20)
    body_text = factory.Faker("paragraph", nb_sentences=5)
    project = factory.LazyFunction(lambda: Project.objects.get_or_create(year=2020)[0])
    recipient_selection = Message.ALL

    class Meta:
        model = Message
