import graphene
from django.apps import apps
from django.db import transaction
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import staff_member_required
from graphql_relay import from_global_id

from common.utils import update_object, update_object_with_translations
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
    def get_queryset(cls, queryset, info):
        return queryset.order_by("-created_at")

    @classmethod
    def get_node(cls, info, id):
        return super().get_node(info, id)


class OccurrenceNode(DjangoObjectType):
    venue_id = graphene.GlobalID()
    event_id = graphene.GlobalID()
    time = graphene.DateTime()

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.order_by("-created_at")

    @classmethod
    def get_node(cls, info, id):
        return super().get_node(info, id)

    class Meta:
        model = Occurrence
        interfaces = (relay.Node,)


class EventTranslationsInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    short_description = graphene.String()
    description = graphene.String()
    language_code = graphene.String(required=True)


class AddEventMutation(graphene.relay.ClientIDMutation):
    class Input:
        translations = graphene.List(EventTranslationsInput)
        duration = graphene.Int()
        participants_per_invite = graphene.String(required=True)
        capacity_per_occurrence = graphene.Int(required=True)
        published_at = graphene.DateTime()
        image = Upload()

    event = graphene.Field(EventNode)

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Add validation
        event = Event.objects.create_translatable_object(**kwargs)
        return AddEventMutation(event=event)


class UpdateEventMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID(required=True)
        duration = graphene.Int()
        participants_per_invite = graphene.String()
        capacity_per_occurrence = graphene.Int()
        published_at = graphene.DateTime()

        translations = graphene.List(EventTranslationsInput)
        delete_translations = graphene.List(graphene.String)

    event = graphene.Field(EventNode)

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Add validation
        event_global_id = kwargs.pop("id")
        try:
            event = Event.objects.get(pk=from_global_id(event_global_id)[1])
            update_object_with_translations(event, kwargs)
        except Event.DoesNotExist as e:
            raise KukkuuGraphQLError(e)
        return UpdateEventMutation(event=event)


class DeleteEventMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Validate data
        event_id = from_global_id(kwargs["id"])[1]
        try:
            event = Event.objects.get(pk=event_id)
            event.delete()
        except Event.DoesNotExist as e:
            raise KukkuuGraphQLError(e)
        return DeleteEventMutation()


class AddOccurrenceMutation(graphene.relay.ClientIDMutation):
    class Input:
        time = graphene.DateTime(required=True)
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
            Event.objects.get(pk=event_id)
            kwargs["event_id"] = event_id
        except Event.DoesNotExist as e:
            raise KukkuuGraphQLError(e)

        venue_id = from_global_id(kwargs["venue_id"])[1]
        try:
            Venue.objects.get(pk=venue_id)
            kwargs["venue_id"] = venue_id
        except Venue.DoesNotExist as e:
            raise KukkuuGraphQLError(e)

        occurrence = Occurrence.objects.create(**kwargs)
        return AddOccurrenceMutation(occurrence=occurrence)


class UpdateOccurrenceMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID(required=True)
        time = graphene.DateTime()
        event_id = graphene.GlobalID()
        venue_id = graphene.GlobalID()

    occurrence = graphene.Field(OccurrenceNode)

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Validate data
        occurrence_id = from_global_id(kwargs["id"])[1]
        try:
            occurrence = Occurrence.objects.get(pk=occurrence_id)
            kwargs["id"] = occurrence_id
        except Occurrence.DoesNotExist as e:
            raise KukkuuGraphQLError(e)

        if kwargs.get("event_id", None):
            event_id = from_global_id(kwargs["event_id"])[1]
            try:
                Event.objects.get(pk=event_id)
                kwargs["event_id"] = event_id
            except Event.DoesNotExist as e:
                raise KukkuuGraphQLError(e)

        if kwargs.get("venue_id", None):
            venue_id = from_global_id(kwargs["venue_id"])[1]
            try:
                Venue.objects.get(pk=venue_id)
                kwargs["venue_id"] = venue_id
            except Venue.DoesNotExist as e:
                raise KukkuuGraphQLError(e)

        update_object(occurrence, kwargs)
        return UpdateOccurrenceMutation(occurrence=occurrence)


class DeleteOccurrenceMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID(required=True)

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Validate data
        occurrence_id = from_global_id(kwargs["id"])[1]
        try:
            occurrence = Occurrence.objects.get(pk=occurrence_id)
            occurrence.delete()
        except Occurrence.DoesNotExist as e:
            raise KukkuuGraphQLError(e)
        return DeleteOccurrenceMutation()


class Query:
    events = DjangoConnectionField(EventNode)
    occurrences = DjangoConnectionField(OccurrenceNode)

    event = relay.Node.Field(EventNode)
    occurrence = relay.Node.Field(OccurrenceNode)


class Mutation:
    add_event = AddEventMutation.Field()
    update_event = UpdateEventMutation.Field()
    delete_event = DeleteEventMutation.Field()

    add_occurrence = AddOccurrenceMutation.Field()
    update_occurrence = UpdateOccurrenceMutation.Field()
    delete_occurrence = DeleteOccurrenceMutation.Field()
