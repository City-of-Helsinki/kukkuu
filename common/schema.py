import graphene
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
