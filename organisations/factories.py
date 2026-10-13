from uuid import UUID

import factory

from organisations.models import Organisation

DEFAULT_ORGANISATION_ID = UUID("54760fde-aa33-49d7-ba47-8bf9fc83d1e1")


class OrganisationFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("company")
    is_system = False

    class Meta:
        model = Organisation
        django_get_or_create = ("name",)

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        if kwargs.get("is_system"):
            existing = model_class.objects.filter(is_system=True).first()
            if existing:
                if "name" in kwargs and kwargs["name"] != existing.name:
                    existing.name = kwargs["name"]
                    existing.save(update_fields=["name"])
                return existing
        return super()._get_or_create(model_class, *args, **kwargs)
