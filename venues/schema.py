import graphene
from django.apps import apps
from django.db import transaction
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphql_jwt.decorators import staff_member_required
from graphql_relay import from_global_id

from common.utils import update_object_with_translations
from kukkuu.exceptions import KukkuuGraphQLError
from venues.models import Venue

VenueTranslation = apps.get_model("venues", "VenueTranslation")


class VenueTranslationType(DjangoObjectType):
    class Meta:
        model = VenueTranslation
        exclude = ("id", "master")


class VenueNode(DjangoObjectType):
    class Meta:
        model = Venue
        interfaces = (relay.Node,)

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.order_by("-created_at")

    @classmethod
    def get_node(cls, info, id):
        return super().get_node(info, id)


class VenueTranslationsInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String()
    language_code = graphene.String(required=True)
    address = graphene.String()
    accessibility_info = graphene.String()
    arrival_instructions = graphene.String()
    additional_info = graphene.String()
    www_url = graphene.String()


class AddVenueMutation(graphene.relay.ClientIDMutation):
    class Input:
        translations = graphene.List(VenueTranslationsInput)

    venue = graphene.Field(VenueNode)

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Add validation
        venue = Venue.objects.create_translatable_object(**kwargs)
        return AddVenueMutation(venue=venue)


class UpdateVenueMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID(required=True)
        translations = graphene.List(VenueTranslationsInput)
        delete_translations = graphene.List(graphene.String)

    venue = graphene.Field(VenueNode)

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Add validation
        venue_global_id = kwargs.pop("id")
        try:
            venue = Venue.objects.get(pk=from_global_id(venue_global_id)[1])
            update_object_with_translations(venue, kwargs)
        except Venue.DoesNotExist as e:
            raise KukkuuGraphQLError(e)
        return UpdateVenueMutation(venue=venue)


class DeleteVenueMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Validate data
        venue_id = from_global_id(kwargs["id"])[1]
        try:
            venue = Venue.objects.get(pk=venue_id)
            venue.delete()
        except Venue.DoesNotExist as e:
            raise KukkuuGraphQLError(e)
        return DeleteVenueMutation()


class Query:
    venue = relay.Node.Field(VenueNode)
    venues = DjangoConnectionField(VenueNode)


class Mutation:
    add_venue = AddVenueMutation.Field()
    update_venue = UpdateVenueMutation.Field()
    delete_venue = DeleteVenueMutation.Field()
