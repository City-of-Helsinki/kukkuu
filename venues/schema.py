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
    language_code = graphene.String()


class VenueInput(graphene.InputObjectType):
    translations = graphene.List(VenueTranslationsInput)
    seat_count = graphene.Int()


class AddVenueMutation(graphene.relay.ClientIDMutation):
    class Input:
        translations = graphene.List(VenueTranslationsInput)
        seat_count = graphene.Int()

    venue = graphene.Field(VenueNode)

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Add validation
        translations = kwargs.pop("translations")
        venue = Venue.objects.create(**kwargs)
        for translation in translations:
            venue_translation = VenueTranslation(master=venue, **translation)
            venue_translation.save()
        return AddVenueMutation(venue=venue)


class Query:
    venue = relay.Node.Field(VenueNode)
    venues = DjangoConnectionField(VenueNode)


class Mutation:
    add_venue = AddVenueMutation.Field()
