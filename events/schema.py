import graphene
from django.apps import apps
from django.db import transaction
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphql_jwt.decorators import login_required, staff_member_required

from events.models import Event, Occurrence
from venues.schema import VenueInput, VenueNode

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


class EventTranslationsInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    short_description = graphene.String()
    description = graphene.String()
    language_code = graphene.String()


class EventInput(graphene.InputObjectType):
    translations = graphene.List(EventTranslationsInput)
    duration = graphene.Int()


class AddEventMutation(graphene.relay.ClientIDMutation):
    class Input:
        translations = graphene.List(EventTranslationsInput)
        duration = graphene.Int()

    event = graphene.Field(EventNode)

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Add validation
        translations = kwargs.pop("translations")
        event = Event.objects.create(**kwargs)
        for translation in translations:
            event_translation = EventTranslation(master=event, **translation)
            event_translation.save()
        return AddEventMutation(event=event)


class AddOccurrenceMutation(graphene.relay.ClientIDMutation):
    class Input:
        time = graphene.DateTime()
        event = EventInput()
        venue = VenueInput()

    occurrence = graphene.Field(OccurrenceNode)

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        event = Event.objects.create(**kwargs)
        return AddEventMutation(event=event)


class Query:
    events = DjangoConnectionField(EventNode)
    occurrences = DjangoConnectionField(OccurrenceNode)

    event = relay.Node.Field(EventNode)
    occurrence = relay.Node.Field(OccurrenceNode)


class Mutation:
    add_event = AddEventMutation.Field()
    add_occurrence = AddOccurrenceMutation.Field()
