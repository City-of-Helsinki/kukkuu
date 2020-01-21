import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.managers import TranslatableQuerySet as ParlerTranslatableQuerySet
from parler.models import TranslatableModel as ParlerTranslatableModel


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("updated_at"), auto_now=True)

    class Meta:
        abstract = True


class UUIDPrimaryKeyModel(models.Model):
    id = models.UUIDField(
        verbose_name=_("UUID"), primary_key=True, default=uuid.uuid4, editable=False
    )

    class Meta:
        abstract = True


class TranslatableQuerySet(ParlerTranslatableQuerySet):
    def create_translatable_object(self, **kwargs):
        translations = kwargs.pop("translations")
        obj = self.create(**kwargs)
        for translation in translations:
            language_code = translation.pop("language_code")
            obj.create_translation(language_code=language_code, **translation)
        return obj


class TranslatableModel(ParlerTranslatableModel):
    objects = TranslatableQuerySet.as_manager()

    class Meta:
        abstract = True
