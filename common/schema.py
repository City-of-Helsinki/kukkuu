import graphene
from django.conf import settings
from django.core.exceptions import PermissionDenied
from graphene_django import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField

from common.utils import get_node_id_from_global_id, get_obj_from_global_id
from kukkuu.exceptions import ApiUsageError
from languages.models import Language
from projects.models import Project, ProjectPermission

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


class ViewFamiliesPermissionRequiredMixin:
    """
    Mixin to be used in connection resolvers to forbid access to the resource
    if the current user does not have the permission to view families globally
    or in the given project (specified by project_id keyword argument, graphene
    should map this from projectId argument to Pythonesque project_id).

    Can be used with e.g. DjangoFilterConnectionField and DjangoConnectionField.

    :raises django.core.exceptions.PermissionDenied:
        If the user does not have the permission to view families.
    """

    @classmethod
    def connection_resolver(
        cls,
        resolver,
        connection,
        default_manager,
        queryset_resolver,
        max_limit,
        enforce_first_or_last,
        root,
        info,
        *args,
        **kwargs,
    ):
        user = info.context.user
        try:
            project_id = get_node_id_from_global_id(kwargs["project_id"], "ProjectNode")
            project = Project.objects.get(id=project_id)
        except (KeyError, Project.DoesNotExist):
            can_view_families = user.is_authenticated and user.has_global_permission(
                ProjectPermission.VIEW_FAMILIES
            )
        else:
            can_view_families = (
                user.is_authenticated and user.can_view_families_in_project(project)
            )

        if not can_view_families:
            raise PermissionDenied("You do not have permission to view families.")

        return super().connection_resolver(
            resolver,
            connection,
            default_manager,
            queryset_resolver,
            max_limit,
            enforce_first_or_last,
            root,
            info,
            *args,
            **kwargs,
        )


class ViewFamiliesPermissionRequiredFilterOffsetConnectionField(
    ViewFamiliesPermissionRequiredMixin, DjangoFilterAndOffsetConnectionField
):
    """
    DjangoFilterAndOffsetConnectionField that requires the user to have the permission
    to view families in the given project (specified with optional projectId parameter)
    or globally, or permission is denied.
    """


class ViewFamiliesPermissionRequiredConnectionField(
    ViewFamiliesPermissionRequiredMixin, DjangoConnectionField
):
    """
    DjangoConnectionField that requires the user to have the permission
    to view families in the given project (specified with optional projectId parameter)
    or globally, or permission is denied.
    """
