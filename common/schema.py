import graphene

# from graphene_django.utils import camelize
from django.conf import settings

from common.utils import get_obj_from_global_id
from languages.models import Language

LanguageEnum = graphene.Enum(
    "Language", [(l[0].upper(), l[0]) for l in settings.LANGUAGES]
)


def set_obj_languages_spoken_at_home(info, obj, language_global_ids):
    obj.languages_spoken_at_home.clear()

    for language_global_id in language_global_ids:
        obj.languages_spoken_at_home.add(
            get_obj_from_global_id(info, language_global_id, Language)
        )


class ErrorType(graphene.ObjectType):
    """
    A geric error type that can be used to add errors inside the data,
    when using the errors field from the root is not possible.

    NOTE: Normally the errors should be added in the errors field
    which is located in the root of the query, next to data, but in some cases,
    e.g. with mutation input errors (without exception thrown),
    the error messages meta class field is not available
    """

    field = graphene.String(required=True)
    message = graphene.String(required=True)
    value = graphene.String(required=True)

    # @staticmethod
    # def serialize(errors):
    #     if isinstance(errors, dict):
    #         if errors.get("__all__", False):
    #             errors["non_field_errors"] = errors.pop("__all__")
    #         return camelize(errors)
    #     raise Exception("`errors` should be dict!")
