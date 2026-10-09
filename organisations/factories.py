from uuid import UUID

import factory

from organisations.models import Organisation

DEFAULT_ORGANISATION_ID = UUID("54760fde-aa33-49d7-ba47-8bf9fc83d1e1")


class OrganisationFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("company")

    class Meta:
        model = Organisation
        django_get_or_create = ("name",)
