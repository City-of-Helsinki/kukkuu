import factory

from projects.models import Project


class ProjectFactory(factory.django.DjangoModelFactory):
    year = factory.Faker("year")

    class Meta:
        model = Project
