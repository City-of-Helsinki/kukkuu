import graphene
from django.conf import settings
from graphene_django.filter import DjangoFilterConnectionField

from common.utils import get_obj_from_global_id
from kukkuu.exceptions import ApiUsageError
from languages.models import Language

LanguageEnum = graphene.Enum(
    "Language", [(lang[0].upper(), lang[0]) for lang in settings.LANGUAGES]
)


def set_obj_languages_spoken_at_home(info, obj, language_global_ids):
    obj.languages_spoken_at_home.clear()

    for language_global_id in language_global_ids:
        obj.languages_spoken_at_home.add(
            get_obj_from_global_id(info, language_global_id, Language)
        )


class ErrorType(graphene.ObjectType):
    """
    A generic error type that can be used to add errors inside the data,
    when using the errors field from the root is not possible.

    NOTE: Normally the errors should be added in the errors field
    which is located in the root of the query, next to data, but in some cases,
    e.g. with mutation input errors (without exception thrown),
    the error messages meta class field is not available
    """

    field = graphene.String(required=True)
    message = graphene.String(required=True)
    value = graphene.String(required=True)


class DjangoFilterAndOffsetConnectionField(DjangoFilterConnectionField):
    def __init__(self, type, *args, **kwargs):
        kwargs.setdefault("limit", graphene.Int())
        kwargs.setdefault("offset", graphene.Int())
        super().__init__(type, *args, **kwargs)

    @classmethod
    def connection_resolver(cls, *args, **kwargs):
        limit = kwargs.get("limit")
        has_cursor = any(arg in kwargs for arg in ("first", "last", "after", "before"))
        if limit:
            if has_cursor:
                raise ApiUsageError("Cannot use both offset and cursor pagination.")
            kwargs["first"] = limit
        return super().connection_resolver(*args, **kwargs)
