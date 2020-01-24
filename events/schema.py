import graphene
from django.apps import apps
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphql_jwt.decorators import login_required

from events.models import Event, Occurrence
from venues.schema import VenueNode

EventTranslation = apps.get_model("events", "EventTranslation")


class EventTranslationType(DjangoObjectType):
    class Meta:
        model = EventTranslation
        exclude = ("id", "master")


class EventNode(DjangoObjectType):
    class Meta:
        model = Event
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    # TODO: For now only logged in users can see events
    def get_queryset(cls, queryset, info):
        return queryset.order_by("-created_at")

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return super().get_node(info, id)


class OccurrenceNode(DjangoObjectType):
    venue = graphene.Field(VenueNode)
    event = graphene.Field(EventNode)

    @classmethod
    @login_required
    # TODO: For now only logged in users can see occurrences
    def get_queryset(cls, queryset, info):
        return queryset.order_by("-created_at")

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return super().get_node(info, id)

    class Meta:
        model = Occurrence
        interfaces = (relay.Node,)


class Query:
    events = DjangoConnectionField(EventNode)
    occurrences = DjangoConnectionField(OccurrenceNode)

    event = relay.Node.Field(EventNode)
    occurrence = relay.Node.Field(OccurrenceNode)
