import graphene
from django.apps import apps
from graphene import ObjectType, relay
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphql_jwt.decorators import login_required
from projects.models import Project

from common.schema import LanguageEnum

ProjectTranslation = apps.get_model("projects", "ProjectTranslation")


class ProjectPermissionsType(ObjectType):
    publish = graphene.Boolean()

    @staticmethod
    def resolve_publish(parent, info):
        project, user = parent
        return user.can_publish_in_project(project)


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
        fields = ("id", "year", "translations", "name", "my_permissions")

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
