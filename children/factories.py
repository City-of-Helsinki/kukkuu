import factory

from children.models import Child, Relationship
from projects.models import Project
from users.factories import GuardianFactory


class ChildFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    birthyear = factory.Faker(
        "random_int", min=2018, max=2023
    )  # NOTE: Many of the tests are freezed to 2020
    postal_code = factory.Faker("postcode", locale="fi_FI")
    project = factory.LazyFunction(lambda: Project.objects.get(year=2020))
    notes = factory.Faker(
        "random_element",
        elements=[
            "",
            "Test notes",
            "Alternative test notes",
            "Longer test notes\nwith multiple lines.",
        ],
    )

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
