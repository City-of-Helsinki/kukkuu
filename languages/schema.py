import graphene
from django.apps import apps
from django.db.models import Count, Prefetch
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from languages.models import Language

LanguageTranslation = apps.get_model("languages", "LanguageTranslation")


class LanguageTranslationType(DjangoObjectType):
    class Meta:
        model = LanguageTranslation
        exclude = ("id", "master")


class LanguageNode(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = Language
        interfaces = (relay.Node,)
        fields = ("alpha_3_code", "name", "translations")

    @classmethod
    def get_queryset(cls, queryset, info):
        return (
            queryset.prefetch_related(
                Prefetch(
                    "translations",
                    queryset=LanguageTranslation.objects.order_by("language_code"),
                )
            )
            .translated()
            .annotate(has_code=Count("alpha_3_code"))  # to order null codes as last
            .order_by("-has_code", "translations__name", "id")
        )


class Query:
    language = relay.Node.Field(LanguageNode)
    languages = DjangoConnectionField(LanguageNode)
