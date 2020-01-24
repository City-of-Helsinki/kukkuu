import graphene
from django.apps import apps
from django.db import transaction
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphql_jwt.decorators import login_required, staff_member_required
from graphql_relay import from_global_id

from events.models import Event, Occurrence
from kukkuu.exceptions import KukkuuGraphQLError
from venues.models import Venue

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
    venue_id = graphene.GlobalID()
    event_id = graphene.GlobalID()
    time = graphene.DateTime()

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


# class EventInput(graphene.InputObjectType):
#     id = graphene.GlobalID()
#     translations = graphene.List(EventTranslationsInput)
#     duration = graphene.Int()
#     participants_per_invite = graphene.String()
#     capacity_per_occurrence = graphene.Int()


class AddEventMutation(graphene.relay.ClientIDMutation):
    class Input:
        translations = graphene.List(EventTranslationsInput)
        duration = graphene.Int()
        participants_per_invite = graphene.String(required=True)
        capacity_per_occurrence = graphene.Int(required=True)
        published_at = graphene.DateTime()

    event = graphene.Field(EventNode)

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Add validation
        event = Event.objects.create_translatable_object(**kwargs)
        # TODO: Add support for image upload
        return AddEventMutation(event=event)


class AddOccurrenceMutation(graphene.relay.ClientIDMutation):
    class Input:
        time = graphene.DateTime()
        event_id = graphene.GlobalID(required=True)
        venue_id = graphene.GlobalID(required=True)

    occurrence = graphene.Field(OccurrenceNode)

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Validate data
        event_id = from_global_id(kwargs["event_id"])[1]
        try:
            event = Event.objects.get(pk=event_id)
            kwargs["event_id"] = event_id
        except Event.DoesNotExist as e:
            raise KukkuuGraphQLError(e)

        venue_id = from_global_id(kwargs["venue_id"])[1]
        try:
            venue = Venue.objects.get(pk=venue_id)
            kwargs["venue_id"] = venue_id
        except Venue.DoesNotExist as e:
            raise KukkuuGraphQLError(e)

        occurrence = Occurrence.objects.create(**kwargs, event=event, venue=venue)
        return AddOccurrenceMutation(occurrence=occurrence)


class Query:
    events = DjangoConnectionField(EventNode)
    occurrences = DjangoConnectionField(OccurrenceNode)

    event = relay.Node.Field(EventNode)
    occurrence = relay.Node.Field(OccurrenceNode)


class Mutation:
    add_event = AddEventMutation.Field()
    add_occurrence = AddOccurrenceMutation.Field()
