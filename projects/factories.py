import factory

from projects.models import Project


class ProjectFactory(factory.django.DjangoModelFactory):
    year = factory.Faker("year")

    class Meta:
        model = Project
        skip_postgeneration_save = True  # Not needed after factory v4.0.0
