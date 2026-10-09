from uuid import UUID, uuid4

import factory

from organisations.models import Organisation

DEFAULT_ORGANISATION_ID = UUID("54760fde-aa33-49d7-ba47-8bf9fc83d1e1")


class OrganisationFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("company")
    id = factory.LazyAttribute(
        lambda o: (
            DEFAULT_ORGANISATION_ID
            if o.name == "Default Test Organisation"
            else uuid4()
        )
    )

    class Meta:
        model = Organisation
        django_get_or_create = ("name",)
