import graphene
from django.apps import apps
from django.db.models import Prefetch
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from common.schema import LanguageEnum
from tags.models import Accessibility, ThemePath

AccessibilityTranslation = apps.get_model("tags", "AccessibilityTranslation")
ThemePathTranslation = apps.get_model("tags", "ThemePathTranslation")


class AccessibilityTranslationType(DjangoObjectType):
    language_code = LanguageEnum(required=True)

    class Meta:
        model = AccessibilityTranslation
        exclude = ("id", "master")


class ThemePathTranslationType(DjangoObjectType):
    language_code = LanguageEnum(required=True)

    class Meta:
        model = ThemePathTranslation
        exclude = ("id", "master")


class TagNode(DjangoObjectType):
    name = graphene.String(required=True)
    description = graphene.String(required=True)

    class Meta:
        abstract = True

    @classmethod
    def get_queryset(cls, queryset, info):
        translation_model = queryset.model._meta.get_field("translations").related_model
        return queryset.prefetch_related(
            Prefetch(
                "translations",
                queryset=translation_model.objects.order_by("language_code"),
            )
        )

    def resolve_name(self, info):
        return str(self)

    def resolve_description(self, info):
        return self.get_translated_value("description", default="")


class ThemePathNode(TagNode):
    class Meta:
        model = ThemePath
        interfaces = (relay.Node,)
        fields = ("slug", "sort_order", "name", "description", "translations")


class AccessibilityNode(TagNode):
    class Meta:
        model = Accessibility
        interfaces = (relay.Node,)
        fields = ("slug", "sort_order", "name", "description", "translations")


class Query:
    theme_path = relay.Node.Field(ThemePathNode)
    theme_paths = DjangoConnectionField(ThemePathNode)
    accessibility = relay.Node.Field(AccessibilityNode)
    accessibilities = DjangoConnectionField(AccessibilityNode)
