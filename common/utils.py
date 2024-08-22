import binascii
import enum
from copy import deepcopy
from functools import wraps

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from graphene import Node
from graphql.type import GraphQLResolveInfo
from graphql_relay import from_global_id, to_global_id

from kukkuu import __version__
from kukkuu.exceptions import DataValidationError, ObjectDoesNotExistError
from kukkuu.settings import REVISION


def is_enum_value(value):
    """
    Check if a value is an enum value, e.g. TestEnum.FI
    where TestEnum derives from enum.Enum or graphene.Enum.
    """
    # Works both for enum.Enum and graphene.Enum
    return type(type(value)) is enum.EnumMeta


def safe_test_and_get_enum_value(enum_value):
    return enum_value.value if is_enum_value(enum_value) else enum_value


def update_object(obj, data):
    if not data:
        return
    for k, v in data.items():
        if v is None and not obj.__class__._meta.get_field(k).null:
            raise DataValidationError(f"{k} cannot be null.")
        setattr(obj, k, safe_test_and_get_enum_value(v))
    obj.save()


@transaction.atomic
def update_object_with_translations(model, model_data):
    model_data = deepcopy(model_data)
    translations_input = model_data.pop("translations", None)
    if translations_input:
        model.create_or_update_translations(translations_input)
    update_object(model, model_data)


def get_api_version():
    return " | ".join((__version__, REVISION))


def get_global_id(obj):
    return to_global_id(f"{obj.__class__.__name__}Node", str(obj.pk))


def get_node_id_from_global_id(global_id, expected_node_name):
    if not global_id:
        return None
    try:
        name, id = from_global_id(global_id)
    except (
        binascii.Error,
        UnicodeDecodeError,
    ):  # invalid global ID
        return None
    return id if name == expected_node_name else None


def check_can_user_administer(obj, user):
    try:
        yes_we_can = obj.can_user_administer(user)
    except AttributeError:
        raise TypeError(
            f"{obj.__class__.__name__} model does not implement can_user_administer()."
        )
    if not yes_we_can:
        raise PermissionDenied()


def get_obj_from_global_id(info, global_id, expected_obj_type):
    obj = Node.get_node_from_global_id(info, global_id)
    if not obj or type(obj) is not expected_obj_type:
        raise ObjectDoesNotExistError(
            f"{expected_obj_type.__name__} with ID {global_id} does not exist."
        )
    return obj


def get_obj_if_user_can_administer(info, global_id, expected_obj_type):
    obj = get_obj_from_global_id(info, global_id, expected_obj_type)
    check_can_user_administer(obj, info.context.user)
    return obj


def context(f):
    def decorator(func):
        def wrapper(*args, **kwargs):
            info = next(arg for arg in args if isinstance(arg, GraphQLResolveInfo))
            return func(info.context, *args, **kwargs)

        return wrapper

    return decorator


def user_passes_test(test_func):
    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):
            if test_func(context.user):
                return f(*args, **kwargs)
            raise PermissionDenied("You do not have permission to perform this action")

        return wrapper

    return decorator


# copied from https://github.com/flavors/django-graphql-jwt/blob/704f24e7ebbea0b81015ef3c1f4a302e9d432ecf/graphql_jwt/decorators.py  # noqa
login_required = user_passes_test(lambda u: u.is_authenticated)

project_user_required = user_passes_test(
    lambda u: u.is_authenticated and u.administered_projects
)


def get_translations_dict(obj, field_name):
    """
    Returns a dict of translations for a given field of a model instance.

    :param obj: The model instance
    :param field_name: The name of the field
    :return: A dict with language codes as keys and translations as values
    """

    return {
        lang_code: getattr(
            obj.translations.filter(language_code=lang_code).first(), field_name, ""
        )
        for lang_code, _ in settings.LANGUAGES
    }


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))
