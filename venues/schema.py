import graphene
from django.apps import apps
from django.db import transaction
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphql_jwt.decorators import login_required, staff_member_required

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
    @login_required
    # TODO: For now only logged in users can see venues
    def get_queryset(cls, queryset, info):
        return queryset.order_by("-created_at")

    @classmethod
    @login_required
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


class VenueInput(graphene.InputObjectType):
    id = graphene.GlobalID()
    translations = graphene.List(VenueTranslationsInput)


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


class Query:
    venue = relay.Node.Field(VenueNode)
    venues = DjangoConnectionField(VenueNode)


class Mutation:
    add_venue = AddVenueMutation.Field()
