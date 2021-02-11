import binascii
from copy import deepcopy

from django.db import transaction
from graphene import Node
from graphql_jwt.decorators import user_passes_test
from graphql_jwt.exceptions import PermissionDenied
from graphql_relay import from_global_id, to_global_id

from kukkuu import __version__
from kukkuu.exceptions import DataValidationError, ObjectDoesNotExistError
from kukkuu.settings import REVISION


def update_object(obj, data):
    if not data:
        return
    for k, v in data.items():
        if v is None and not obj.__class__._meta.get_field(k).null:
            raise DataValidationError(f"{k} cannot be null.")
        setattr(obj, k, v)
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
    return to_global_id(f"{obj.__class__.__name__}Node", obj.pk)


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
    if not obj or type(obj) != expected_obj_type:
        raise ObjectDoesNotExistError(
            f"{expected_obj_type.__name__} with ID {global_id} does not exist."
        )
    return obj


def get_obj_if_user_can_administer(info, global_id, expected_obj_type):
    obj = get_obj_from_global_id(info, global_id, expected_obj_type)
    check_can_user_administer(obj, info.context.user)
    return obj


project_user_required = user_passes_test(
    lambda u: u.is_authenticated and u.administered_projects
)
