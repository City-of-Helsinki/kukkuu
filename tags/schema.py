import graphene
from django.apps import apps
from django.db.models import Prefetch
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from common.schema import LanguageEnum
from tags.models import ThemePath

ThemePathTranslation = apps.get_model("tags", "ThemePathTranslation")


class ThemePathTranslationType(DjangoObjectType):
    language_code = LanguageEnum(required=True)

    class Meta:
        model = ThemePathTranslation
        exclude = ("id", "master")


class ThemePathNode(DjangoObjectType):
    name = graphene.String(required=True)
    description = graphene.String(required=True)

    class Meta:
        model = ThemePath
        interfaces = (relay.Node,)
        fields = ("slug", "sort_order", "name", "description", "translations")

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.prefetch_related(
            Prefetch(
                "translations",
                queryset=ThemePathTranslation.objects.order_by("language_code"),
            )
        )

    def resolve_name(self, info):
        return str(self)

    def resolve_description(self, info):
        return self.get_translated_value("description", default="")


class Query:
    theme_path = relay.Node.Field(ThemePathNode)
    theme_paths = DjangoConnectionField(ThemePathNode)
