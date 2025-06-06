import graphene
from django.apps import apps
from graphene import ObjectType, relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from common.schema import LanguageEnum
from common.utils import login_required
from projects.models import Project

ProjectTranslation = apps.get_model("projects", "ProjectTranslation")


class ProjectPermissionsType(ObjectType):
    publish = graphene.Boolean()
    manage_event_groups = graphene.Boolean()
    can_send_to_all_in_project = graphene.Boolean()
    view_families = graphene.Boolean()

    @staticmethod
    def resolve_publish(parent, info):
        project, user = parent
        return user.can_publish_in_project(project)

    @staticmethod
    def resolve_manage_event_groups(parent, info):
        project, user = parent
        return user.can_manage_event_groups_in_project(project)

    @staticmethod
    def resolve_can_send_to_all_in_project(parent, info):
        project, user = parent
        return user.can_send_messages_to_all_in_project(project)

    @staticmethod
    def resolve_view_families(parent, info):
        project, user = parent
        return user.can_view_families_in_project(project)


class ProjectTranslationType(DjangoObjectType):
    language_code = LanguageEnum(required=True)

    class Meta:
        model = ProjectTranslation
        fields = ("name", "language_code")


class ProjectNode(DjangoObjectType):
    name = graphene.String()
    my_permissions = graphene.Field(ProjectPermissionsType)

    class Meta:
        model = Project
        interfaces = (relay.Node,)
        fields = (
            "id",
            "year",
            "translations",
            "name",
            "my_permissions",
            "single_events_allowed",
            "enrolment_limit",
        )

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return super().get_node(info, id)

    @staticmethod
    @login_required
    def resolve_my_permissions(parent, info):
        return parent, info.context.user


class Query:
    projects = DjangoConnectionField(ProjectNode)
    project = relay.Node.Field(ProjectNode)
