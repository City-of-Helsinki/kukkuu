import factory

from children.models import Child, Relationship
from projects.models import Project
from users.factories import GuardianFactory


class ChildFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    birthdate = factory.Faker("date_this_year", before_today=True, after_today=False)
    postal_code = factory.Faker("postcode", locale="fi_FI")
    project = factory.LazyFunction(lambda: Project.objects.get(year=2020))

    class Meta:
        model = Child


class RelationshipFactory(factory.django.DjangoModelFactory):
    child = factory.SubFactory(ChildFactory)
    guardian = factory.SubFactory(GuardianFactory)
    type = factory.Faker(
        "random_element", elements=[t[0] for t in Relationship.TYPE_CHOICES]
    )

    class Meta:
        model = Relationship


class ChildWithGuardianFactory(ChildFactory):
    relationship = factory.RelatedFactory(RelationshipFactory, "child")
    project = factory.LazyFunction(lambda: Project.objects.get(year=2020))


class ChildWithTwoGuardiansFactory(ChildWithGuardianFactory):
    relationship2 = factory.RelatedFactory(RelationshipFactory, "child")
